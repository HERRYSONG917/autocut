#!/usr/bin/env python3
"""Read-only local media intake. Python 3.9+; ffprobe is optional.

Examples:
  python3 prepare_job.py doctor
  python3 prepare_job.py prepare ./素材 --output ./job
  python3 prepare_job.py prepare ./素材 --output ./job --rehash

Cached hashes use size + nanosecond mtime, which is a speed heuristic, not
cryptographic verification. --rehash rereads every file and reruns probes.
Symlinks are skipped. Originals are never copied, edited, played, or uploaded.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


VIDEO = set(".mp4 .mov .mkv .avi .webm .m4v .mpg .mpeg .mts .m2ts .ts .wmv .flv .3gp .ogv .vob".split())
AUDIO = set(".wav .mp3 .m4a .aac .flac .ogg .opus .aif .aiff .wma".split())
EXTENSIONS = VIDEO | AUDIO | {".srt"}
MANIFEST = "job-manifest.json"
SCHEMA = 1


def inside(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def enumerate_files(root, output):
    files, skipped, errors = [], [], []
    exclude_output = inside(output, root)

    def walk_error(error):
        path = Path(error.filename or root)
        name = path.relative_to(root).as_posix() if inside(path, root) else "."
        errors.append({"path": name, "error": str(error).replace(str(root), "<INPUT>")})

    for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        keep = []
        for name in sorted(dirs):
            path = base / name
            if exclude_output and inside(path, output):
                continue
            if path.is_symlink():
                skipped.append(path.relative_to(root).as_posix())
            else:
                keep.append(name)
        dirs[:] = keep
        for name in sorted(names):
            path = base / name
            if exclude_output and inside(path, output):
                continue
            if path.is_symlink():
                skipped.append(path.relative_to(root).as_posix())
            elif path.suffix.lower() in EXTENSIONS:
                files.append(path)
    return sorted(files), skipped, errors


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) and result >= 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def probe(path, executable, timeout):
    result = {"status": "unavailable", "source": "none", "error": None,
              "duration_seconds": None, "resolution": None, "has_audio": None,
              "format_name": None, "streams": []}
    if not executable:
        result["error"] = "ffprobe is not available on PATH"
        return result
    result["source"] = "run"
    command = [executable, "-v", "error", "-protocol_whitelist", "file",
               "-show_entries", "format=duration,format_name:stream=index,codec_type,codec_name,width,height,duration,avg_frame_rate,sample_rate,channels",
               "-of", "json", "-i", str(path)]
    try:
        process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout, check=False)
        if process.returncode:
            result.update(status="error", error=process.stderr.decode("utf-8", "replace").replace(str(path), "<media>").strip()[:2000]
                          or "ffprobe exited with code %s" % process.returncode)
            return result
        data = json.loads(process.stdout)
        streams = data.get("streams", [])
        if not isinstance(streams, list) or not all(isinstance(item, dict) for item in streams):
            raise ValueError("invalid streams in ffprobe JSON")
        video = next((s for s in streams if s.get("codec_type") == "video"), None)
        duration = number(data.get("format", {}).get("duration"))
        if duration is None:
            duration = max((n for n in (number(s.get("duration")) for s in streams)
                            if n is not None), default=None)
        resolution = None
        if video and isinstance(video.get("width"), int) and isinstance(video.get("height"), int):
            resolution = {"width": video["width"], "height": video["height"]}
        result.update(status="ok", duration_seconds=duration, resolution=resolution,
                      has_audio=any(s.get("codec_type") == "audio" for s in streams),
                      format_name=data.get("format", {}).get("format_name"), streams=streams)
    except subprocess.TimeoutExpired:
        result.update(status="timeout", error="ffprobe exceeded %s seconds" % timeout)
    except (OSError, ValueError, TypeError) as error:
        result.update(status="error", error=str(error)[:2000])
    return result


def signature(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def inspect_file(path, root, previous, executable, timeout, rehash):
    relative = path.relative_to(root).as_posix()
    category = "video" if path.suffix.lower() in VIDEO else "audio" if path.suffix.lower() in AUDIO else "subtitle"
    entry = {"path": relative, "category": category, "size_bytes": None, "mtime_ns": None,
             "sha256": None, "hash_source": None, "hash_error": None, "probe": None}
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise OSError("not a regular file (symlinks are not followed)")
        entry.update(size_bytes=before.st_size, mtime_ns=before.st_mtime_ns)
        cached = (not rehash and isinstance(previous, dict)
                  and previous.get("size_bytes") == before.st_size
                  and previous.get("mtime_ns") == before.st_mtime_ns)
        if cached and isinstance(previous.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", previous["sha256"]):
            entry.update(sha256=previous["sha256"], hash_source="size_mtime_cache")
        else:
            digest = hashlib.sha256()
            # O_NOFOLLOW additionally protects the final component on supported OSes.
            fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as source:
                if signature(os.fstat(source.fileno())) != signature(before):
                    raise OSError("file changed before hashing; rerun intake")
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            entry.update(sha256=digest.hexdigest(), hash_source="fresh_read")
        prior_probe = previous.get("probe") if cached else None
        if category == "subtitle":
            entry["probe"] = {"status": "not_applicable", "source": "none", "error": None,
                              "duration_seconds": None, "resolution": None, "has_audio": None,
                              "format_name": None, "streams": []}
        elif isinstance(prior_probe, dict) and prior_probe.get("status") == "ok":
            entry["probe"] = dict(prior_probe, source="size_mtime_cache")
        else:
            entry["probe"] = probe(path, executable, timeout)
        if signature(path.lstat()) != signature(before):
            raise OSError("file changed during intake; rerun intake")
    except OSError as error:
        entry.update(sha256=None, hash_source=None, hash_error=str(error).replace(str(path), relative))
        entry["probe"] = None
    return entry


def atomic_json(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".intake-", suffix=".tmp", delete=False) as output:
            temporary = output.name
            json.dump(data, output, ensure_ascii=False, indent=2, allow_nan=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def prepare(args):
    root = Path(args.input).expanduser().resolve(strict=True)
    output = Path(args.output).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("INPUT must be a directory")
    if output == root:
        raise ValueError("OUTPUT must differ from INPUT")
    if output.exists() and not output.is_dir():
        raise ValueError("OUTPUT must be a directory")
    # Keep absolute source paths out of the shareable manifest; this key only
    # prevents accidental cache reuse when one output is used for another input.
    input_key = hashlib.sha256(os.fsencode(str(root))).hexdigest()
    old_entries = {}
    if not args.rehash:
        try:
            old = json.loads((output / MANIFEST).read_text(encoding="utf-8"))
            if old.get("schema_version") == SCHEMA and old.get("input_cache_key") == input_key:
                old_entries = {e["path"]: e for e in old.get("files", []) if isinstance(e, dict) and isinstance(e.get("path"), str)}
        except (OSError, ValueError, AttributeError, TypeError):
            pass
    paths, skipped, errors = enumerate_files(root, output)
    executable = shutil.which("ffprobe")
    entries = [inspect_file(path, root, old_entries.get(path.relative_to(root).as_posix()),
                            executable, args.probe_timeout, args.rehash) for path in paths]
    cached = sum(e["hash_source"] == "size_mtime_cache" for e in entries)
    problems = sum(bool(e["hash_error"]) or (e["probe"] or {}).get("status") not in {"ok", "not_applicable"} for e in entries)
    complete = not errors and all(e["sha256"] for e in entries)
    fingerprint = None
    if complete:
        contents = [[e["path"], e["sha256"]] for e in entries]
        fingerprint = hashlib.sha256(json.dumps(contents, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    status = "warnings" if problems or errors or skipped else "ready" if entries else "empty"
    manifest = {"schema_version": SCHEMA, "created_utc": datetime.now(timezone.utc).isoformat(),
                "input_name": root.name, "input_cache_key": input_key,
                "path_base": "INPUT; file paths preserve original subfolders",
                "status": status, "file_count": len(entries), "cached_hash_count": cached,
                "probe_timeout_seconds": args.probe_timeout,
                "content_fingerprint": {"algorithm": "sha256(relative_path, file_sha256)", "value": fingerprint,
                                        "freshness": "uses_size_mtime_cache" if cached else "fresh_reads",
                                        "complete": complete},
                "cache_note": "Size + mtime cache is a speed heuristic, not cryptographic freshness verification. Use --rehash to reread files and rerun probes.",
                "skipped_symlinks": skipped, "scan_errors": errors, "files": entries}
    output.mkdir(parents=True, exist_ok=True)
    destination = output / MANIFEST
    atomic_json(destination, manifest)
    print("manifest=%s files=%s cached_hashes=%s status=%s" % (destination, len(entries), cached, status))
    return 0


def positive_seconds(value):
    result = float(value)
    if not math.isfinite(result) or not 0 < result <= 120:
        raise argparse.ArgumentTypeError("must be finite and greater than zero, up to 120 seconds")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="report executable availability without inspecting secrets")
    command = commands.add_parser("prepare", help="write a read-only inventory to OUTPUT/job-manifest.json")
    command.add_argument("input", help="existing media directory; original subfolders are preserved")
    command.add_argument("--output", required=True, help="job directory, different from INPUT")
    command.add_argument("--rehash", action="store_true", help="bypass hash/probe cache and reread originals")
    command.add_argument("--probe-timeout", type=positive_seconds, default=20, metavar="SECONDS")
    args = parser.parse_args()
    if args.command == "doctor":
        print("ffmpeg=%s ffprobe=%s" % tuple("available" if shutil.which(name) else "missing" for name in ("ffmpeg", "ffprobe")))
        return 0
    try:
        return prepare(args)
    except (OSError, ValueError) as error:
        print("prepare_job: %s" % error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
