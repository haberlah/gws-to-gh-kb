#!/usr/bin/env python3
"""Normalize markdown exports from Google Workspace and local converters.

The gws CLI can occasionally leave a MIME multipart wrapper around a Google Docs
markdown export. That wrapper is not markdown and breaks downstream frontmatter
and index parsing. This script strips the wrapper when present and otherwise
leaves the file unchanged.
"""
import re
import sys
from pathlib import Path


BOUNDARY_RE = re.compile(r"^--([A-Za-z0-9_.=-]*gws_boundary[A-Za-z0-9_.=-]*)", re.M)


def strip_mime_wrapper(text):
    match = BOUNDARY_RE.search(text)
    if not match:
        return text, False

    boundary = match.group(1)
    chunks = re.split(rf"^--{re.escape(boundary)}(?:--)?\s*$", text, flags=re.M)
    bodies = []
    for chunk in chunks:
        chunk = chunk.strip("\r\n")
        if not chunk:
            continue

        # MIME parts have headers followed by a blank line. If no header block is
        # present, keep the raw chunk as a last-resort candidate.
        if "\n\n" in chunk:
            headers, body = chunk.split("\n\n", 1)
            if re.search(r"(?im)^content-(type|transfer-encoding):", headers):
                bodies.append(body.strip("\r\n"))
                continue
        bodies.append(chunk.strip("\r\n"))

    markdownish = [
        body for body in bodies
        if body.startswith("---\n")
        or "\n# " in body
        or body.startswith("# ")
        or len(body.split()) > 20
    ]
    if not markdownish:
        return text, False

    # Prefer the part that looks most like actual markdown content.
    return max(markdownish, key=len).rstrip() + "\n", True


def normalize(path):
    p = Path(path)
    text = p.read_text(errors="replace")
    cleaned, changed = strip_mime_wrapper(text)
    if changed:
        p.write_text(cleaned)
        print(f"stripped MIME wrapper: {p}")
    return changed


def main(argv):
    if len(argv) < 2:
        print("Usage: sanitize_markdown.py <markdown-file> [...]", file=sys.stderr)
        return 2

    for item in argv[1:]:
        normalize(item)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
