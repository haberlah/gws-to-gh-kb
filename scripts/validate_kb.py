#!/usr/bin/env python3
"""Validate a generated AI-readable KB before committing or opening a PR."""
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required. Install with: pip3 install pyyaml", file=sys.stderr)
    sys.exit(2)


SKIP_DIRS = {".git", ".claude", "scripts", "__pycache__", "node_modules"}
MIME_MARKERS = (
    "--gws_boundary",
    "Content-Type: multipart/",
    "Content-Transfer-Encoding:",
)


def read_frontmatter(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    try:
        data = yaml.safe_load(text[4:end])
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def iter_files(root):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def main(argv):
    kb_root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    strict = "--strict" in argv
    errors = []
    warnings = []
    empty_provenance = 0
    ids = defaultdict(list)

    for path in iter_files(kb_root):
        rel = path.relative_to(kb_root)
        if path.suffix.lower() != ".md":
            continue

        if path.name.lower().endswith(".md.md"):
            errors.append(f"{rel}: duplicate markdown suffix; likely stale Google Docs export")

        text = path.read_text(errors="replace")
        if any(marker in text[:5000] for marker in MIME_MARKERS):
            errors.append(f"{rel}: contains MIME multipart wrapper/header text")

        fm = read_frontmatter(text)
        doc_id = str(fm.get("google_doc_id") or "").strip()
        doc_url = str(fm.get("google_doc_url") or "").strip()
        if doc_id:
            ids[doc_id].append(rel)
        if "/drive/folders/" in doc_url:
            warnings.append(f"{rel}: google_doc_url points to a Drive folder, not a source document")
        if doc_id and doc_url.endswith(f"/folders/{doc_id}"):
            warnings.append(f"{rel}: google_doc_id appears to be a folder ID")
        if fm and not doc_id:
            empty_provenance += 1

        if "Stage_2_Feature_Validation" in path.name:
            if re.search(r"\|\s*0:05\s*\|\s*5 min\s*\|\s*\*\*Closing \+", text):
                msg = f"{rel}: Stage 2 closing row starts at 0:05 instead of the end slot"
                if str(rel).startswith("co-design/templates/"):
                    errors.append(msg)
                else:
                    warnings.append(msg)

    for doc_id, paths in sorted(ids.items()):
        if len(paths) >= 3:
            joined = ", ".join(str(p) for p in paths[:5])
            warnings.append(f"google_doc_id {doc_id} is reused by {len(paths)} markdown files: {joined}")

    if strict and warnings:
        errors.extend(warnings)
        warnings = []

    if empty_provenance:
        warnings.insert(0, f"{empty_provenance} markdown files have empty google_doc_id")

    if warnings:
        print("KB validation warnings:")
        shown = warnings[:30]
        for item in shown:
            print(f"  WARN: {item}")
        if len(warnings) > len(shown):
            print(f"  WARN: {len(warnings) - len(shown)} additional warnings suppressed")

    if errors:
        print("KB validation failed:")
        for item in errors:
            print(f"  ERROR: {item}")
        return 1

    print(f"KB validation passed: {kb_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
