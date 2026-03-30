# gws-to-gh-kb

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Claude Code skill that backs up Google Drive to a local directory and transforms documents into an AI-readable knowledge base. Google Docs become Markdown, Sheets become CSV, and everything gets YAML frontmatter with a searchable `index.json`. The output is designed to be committed to a Git repository so your team can access organisational knowledge through GitHub MCP tools or direct clone.

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| [gws CLI](https://www.npmjs.com/package/@googleworkspace/cli) | Google Workspace API access | `npm install -g @googleworkspace/cli` |
| `gcloud` | GCP authentication | `brew install google-cloud-sdk` |
| `jq` | JSON processing | `brew install jq` |
| `pandoc` | .docx to Markdown conversion | `brew install pandoc` |
| `openpyxl` | .xlsx to CSV conversion | `pip3 install openpyxl` |
| `pyyaml` | YAML frontmatter generation | `pip3 install pyyaml` |

Verify gws is authenticated:

```bash
gws drive files list --params '{"pageSize": 1}'
```

## Installation

Copy the skill into your Claude Code skills directory:

```bash
cp -r gws-to-gh-kb ~/.claude/skills/gws-to-gh-kb
```

Claude Code will automatically discover the skill from `SKILL.md`.

## Quick start

```bash
# 1. Create backup and KB directories
mkdir -p ~/gws_backup/kb

# 2. Copy configuration templates and customise
cp examples/category_mapping.example.json ~/gws_backup/kb/category_mapping.json
cp examples/skip_patterns.example.json ~/gws_backup/kb/skip_patterns.json
# Edit both files to match your Drive folder structure

# 3. Run the full sync pipeline
bash ~/.claude/skills/gws-to-gh-kb/scripts/sync_kb.sh ~/gws_backup ~/gws_backup/kb

# 4. Initialise the KB as a Git repository
cd ~/gws_backup/kb && git init && git add -A && git commit -m "Initial KB sync"

# 5. Push to GitHub for team access
gh repo create my-org/knowledge-base --private --source . --push
```

## The six-phase pipeline

| Phase | Script | What it does |
|-------|--------|-------------|
| 0 | (inline gws command) | Exports Drive metadata to `drive_metadata.json` |
| 1 | `gws_backup.sh` | Downloads files from Google Drive with native format conversion |
| 2 | `convert_local.py` | Converts .docx to Markdown and .xlsx to CSV |
| 3 | `verify_backup.sh` | Validates completeness — checks for missing conversions and zero-byte files |
| 4 | `populate_kb.py` | Builds the AI-readable KB with category sorting, YAML frontmatter, and sensitivity labels |
| 5 | `sync_kb.sh` | Orchestrates all phases end-to-end and creates a GitHub PR |

Additional scripts:
- `extract_images.py` — decodes base64 images from Google Docs markdown export
- `build_index.py` — generates `index.json` for programmatic catalogue access

See [SKILL.md](SKILL.md) for detailed usage of each phase.

## Configuration

### category_mapping.json

Maps Google Drive folder paths to KB topic directories. Each rule is a regex tested against the file's relative path; first match wins. Files with no match are skipped.

```json
[
  {"pattern": "Architecture/", "category": "architecture"},
  {"pattern": "Strategy/", "category": "strategy"}
]
```

See [`examples/category_mapping.example.json`](examples/category_mapping.example.json) for a starter template.

### skip_patterns.json

Regex patterns for files to exclude from the KB (e.g. duplicates, temporary files):

```json
[
  "Copy_of_.*",
  "~\\$.*"
]
```

See [`examples/skip_patterns.example.json`](examples/skip_patterns.example.json).

## Safety: write-guard hook

The `gws-write-guard.sh` hook prevents Claude Code from accidentally running write operations against your Google Workspace. It intercepts Bash tool calls containing `gws` commands and blocks any that end with a write action (create, update, delete, send, etc.).

Install it by adding the hook to your Claude Code settings at `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash /path/to/hooks/gws-write-guard.sh"
          }
        ]
      }
    ]
  }
}
```

Replace `/path/to/hooks/gws-write-guard.sh` with the actual path (e.g. `~/.claude/hooks/gws-write-guard.sh`).

Read-only operations (list, get, export, search) pass through without interruption. Write operations are blocked with a message requiring explicit user approval before retrying.

## Project-level skills

The `examples/project-skills/` directory contains generic skill templates you can add to your project's `.claude/skills/` directory:

| Skill | Purpose |
|-------|---------|
| `kb-sync` | Admin-only skill to trigger a full Drive-to-KB sync |
| `kb-search` | Search the KB by category, tag, keyword, or sensitivity level |
| `kb-update` | Propose changes to KB documents via pull request |

Copy and customise the paths in each template to match your project layout.

## Team access

The recommended workflow separates admin and reader roles:

1. **Admin** runs `kb-sync` to pull latest content from Google Drive, transform it, and open a PR against the KB repository.
2. **Team members** access the KB read-only through:
   - GitHub MCP `search_code` tool for content search
   - GitHub MCP `get_file_contents` for reading specific documents
   - Direct clone for local access
   - The `kb-search` and `kb-update` project skills

This keeps Drive credentials with the admin while giving the whole team AI-readable access to organisational knowledge.

## License

[MIT](LICENSE)

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request. Bug reports and feature requests are appreciated.

## Related

- [Blog post: From Cloud Folders to Agentic Knowledge Bases](https://medium.com/@haberlah) — the full write-up explaining the architecture and design decisions behind this skill
