#!/usr/bin/env python3
"""Validate SRT without rewriting it. Python 3.9+; no dependencies.

python3 check_srt.py captions.srt --max-cps 22 --max-lines 2 --duration 60

Overlaps, invalid timestamps, and malformed cues are errors (exit 1).
Reading speed and explicit line count are soft warnings (exit 0).
Visual preview is still required to assess rendered wrapping and positioning.
"""

import argparse
import json
import math
from pathlib import Path
import re
import sys


TIMING = re.compile(r"^\s*(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})\s+-->\s+(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})\s*$")


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return number


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def milliseconds(parts):
    hours, minutes, seconds, fraction = map(int, parts)
    result = ((hours * 60 + minutes) * 60 + seconds) * 1000 + fraction
    if not math.isfinite(result / 1000.0):
        raise ValueError("timestamp must be finite")
    return result


def validate(text, max_cps, max_lines, duration):
    issues, ids = [], set()
    previous_start, latest_end, latest_id = None, None, None
    valid_cues, longest_line = 0, 0

    def issue(severity, code, cue_id, block, message):
        issues.append({"severity": severity, "code": code, "cue_id": cue_id,
                       "block": block, "message": message})

    blocks = re.split(r"\n(?:[ \t]*\n)+", text.strip()) if text.strip() else []
    if not blocks:
        issue("error", "empty", None, None, "No SRT cues found")
    for block_number, block in enumerate(blocks, 1):
        lines = block.split("\n")
        cue_id = lines[0].strip() if lines else ""
        if not re.fullmatch(r"[0-9]+", cue_id) or not cue_id.strip("0"):
            issue("error", "cue_id", cue_id or None, block_number, "Cue ID must be a positive integer")
        elif cue_id.lstrip("0") in ids:
            issue("error", "duplicate_id", cue_id, block_number, "Duplicate cue ID")
        else:
            ids.add(cue_id.lstrip("0"))
        if len(lines) < 3 or not any(line.strip() for line in lines[2:]):
            issue("error", "structure", cue_id, block_number, "Expected cue ID, timing line, and nonempty text")
            continue
        match = TIMING.fullmatch(lines[1])
        if not match:
            issue("error", "timestamp", cue_id, block_number, "Expected HH:MM:SS,mmm --> HH:MM:SS,mmm")
            continue
        try:
            start, end = milliseconds(match.groups()[:4]), milliseconds(match.groups()[4:])
        except (ValueError, OverflowError):
            issue("error", "timestamp", cue_id, block_number, "Invalid or nonfinite timestamp")
            continue
        if start >= end:
            issue("error", "duration", cue_id, block_number, "Cue start must be earlier than its end")
            continue
        valid_cues += 1
        if previous_start is not None and start < previous_start:
            issue("error", "order", cue_id, block_number, "Cue starts before the preceding cue")
        if latest_end is not None and start < latest_end:
            issue("error", "overlap", cue_id, block_number, "Overlaps cue %s" % latest_id)
        if duration is not None and end > duration * 1000:
            issue("error", "media_duration", cue_id, block_number, "Cue ends after the supplied media duration")
        previous_start = start
        if latest_end is None or end > latest_end:
            latest_end, latest_id = end, cue_id
        body = lines[2:]
        if any(TIMING.fullmatch(line) for line in body):
            issue("error", "separator", cue_id, block_number, "Timing line inside cue text; a blank cue separator may be missing")
        # Approximate visible characters: strip common HTML and ASS style tags.
        visible = [re.sub(r"<[^>]*>|\{\\[^}]*\}", "", line).strip() for line in body]
        longest_line = max([longest_line] + [len(line) for line in visible])
        cps = len(" ".join(visible)) / ((end - start) / 1000.0)
        if cps > max_cps:
            issue("warning", "reading_speed", cue_id, block_number,
                  "%.1f characters/second exceeds %.1f" % (cps, max_cps))
        if len(body) > max_lines:
            issue("warning", "line_count", cue_id, block_number,
                  "%s explicit lines exceeds %s" % (len(body), max_lines))
    return {"cue_count": len(blocks), "valid_timing_cue_count": valid_cues,
            "maximum_explicit_line_characters": longest_line, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file")
    parser.add_argument("--max-cps", type=positive, default=22)
    parser.add_argument("--max-lines", type=positive_int, default=2)
    parser.add_argument("--duration", type=positive, help="media duration in seconds; enables cue boundary errors")
    args = parser.parse_args()
    try:
        raw = Path(args.file).expanduser().read_bytes()
        text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError:
        print(json.dumps({"status": "error", "issues": [{"severity": "error", "code": "encoding", "cue_id": None,
                                                       "message": "SRT must be UTF-8; UTF-8 BOM is accepted"}]}))
        return 1
    except OSError as error:
        print(json.dumps({"status": "io_error", "error": str(error)}))
        return 2
    result = validate(text, args.max_cps, args.max_lines, args.duration)
    errors = sum(item["severity"] == "error" for item in result["issues"])
    warnings = sum(item["severity"] == "warning" for item in result["issues"])
    result.update(status="error" if errors else "warnings" if warnings else "pass",
                  error_count=errors, warning_count=warnings,
                  utf8_bom=raw.startswith(b"\xef\xbb\xbf"),
                  max_cps=args.max_cps, max_lines=args.max_lines, media_duration_seconds=args.duration,
                  limitation="Text checks only. Visual preview is still required to assess rendered line wrapping and positioning.")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
