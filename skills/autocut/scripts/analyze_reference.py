#!/usr/bin/env python3
"""Measure local scene candidates and mixed-audio quiet spans; never render media.

Python 3.9+, existing FFmpeg with scdet/silencedetect. No cloud calls.
Measurements are review aids, not word alignment or automatic edit decisions.
"""

import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile


def finite_in_range(value, low, high):
    result = float(value)
    if not math.isfinite(result) or not low < result <= high:
        raise argparse.ArgumentTypeError("must be in (%s, %s]" % (low, high))
    return result


def analyze(path, ffmpeg, fps, threshold, timeout, label):
    command = [ffmpeg, "-hide_banner", "-nostdin", "-nostats", "-threads", "2",
               "-filter_threads", "1", "-protocol_whitelist", "file", "-i", str(path),
               "-map", "0:v:0", "-map", "0:a:0?", "-vf",
               "fps=%s,scale=256:-2,scdet=t=%s:sc_pass=1,metadata=mode=print:key=lavfi.scd.time:file=-" % (fps, threshold),
               "-af", "silencedetect=noise=-35dB:d=0.30", "-f", "null", "-"]
    try:
        result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise ValueError("FFmpeg exceeded %s seconds for %s" % (timeout, path.name)) from None
    if result.returncode:
        message = result.stderr.replace(str(path), path.name)[-1600:]
        raise ValueError("FFmpeg failed for %s: %s" % (path.name, message))
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    duration = int(match[1]) * 3600 + int(match[2]) * 60 + float(match[3]) if match else None
    candidates = sorted(set(float(x) for x in re.findall(r"lavfi\.scd\.time=([\d.]+)", result.stdout)))
    quiet, opened = [], None
    for event, value in re.findall(r"silence_(start|end):\s*([\d.]+)", result.stderr):
        if event == "start":
            opened = float(value)
        elif opened is not None:
            quiet.append({"start": round(opened, 3), "end": round(float(value), 3)})
            opened = None
    if opened is not None and duration is not None:
        quiet.append({"start": round(opened, 3), "end": duration})
    boundaries = [0.0] + candidates + ([duration] if duration is not None else [])
    spans = [b-a for a, b in zip(boundaries, boundaries[1:]) if b >= a]
    has_audio = bool(re.search(r"Stream #.*Audio:", result.stderr))
    return {"file": label, "bytes": path.stat().st_size, "duration_seconds": duration,
            "has_audio": has_audio, "scan_fps": fps, "scene_threshold_percent": threshold,
            "scene_candidate_seconds": candidates,
            "median_candidate_span_seconds": round(statistics.median(spans), 3) if spans else None,
            "mixed_audio_quiet_spans": quiet,
            "limits": "Candidate changes may be camera motion, overlays or fades and may miss similar-angle cuts. Precision is limited by scan_fps. Quiet spans use mixed audio at -35 dB for >=0.30 s; music may mask pauses. Not speech VAD, word alignment, OCR or quality certification."}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".analysis-", suffix=".tmp", delete=False) as output:
            temporary = output.name
            json.dump(data, output, ensure_ascii=False, indent=2, allow_nan=False)
            output.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--output", required=True)
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument("--fps", type=lambda v: finite_in_range(v, 0, 30), default=6)
    parser.add_argument("--scene-threshold", type=lambda v: finite_in_range(v, 0, 100), default=8)
    parser.add_argument("--timeout", type=lambda v: finite_in_range(v, 0, 3600), default=120,
                        help="maximum seconds per input; default 120")
    args = parser.parse_args()
    if not args.ffmpeg:
        parser.error("FFmpeg missing; use --ffmpeg with an existing executable. No automatic install.")
    try:
        paths = [Path(p).expanduser().resolve(strict=True) for p in args.inputs]
        if any(not p.is_file() for p in paths):
            raise ValueError("inputs must be local files")
        if len(set(paths)) != len(paths):
            raise ValueError("duplicate input files")
        out = Path(args.output).expanduser().resolve()
        if any(out == p or (out.exists() and os.path.samefile(out, p)) for p in paths):
            raise ValueError("output must not replace or alias an input")
        parent = Path(os.path.commonpath([str(p.parent) for p in paths]))
        records = [analyze(p, args.ffmpeg, args.fps, args.scene_threshold, args.timeout,
                           p.relative_to(parent).as_posix()) for p in paths]
        write_json(out, {"version": 1, "measurements": records})
        print("SCANNED %s file(s); measurements=%s" % (len(records), out.name))
    except (OSError, ValueError) as error:
        print("analyze_reference: %s" % error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
