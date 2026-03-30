---
name: kb-sync
description: ADMIN ONLY — Sync the knowledge base from Google Drive
---

# KB Sync

Runs the full gws-drive-backup pipeline to refresh the local knowledge base from Google Drive and open a pull request with changes.

## Paths

> **CUSTOMISE THESE** to match your project layout.

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKUP_DIR` | `~/gws_backup` | Raw Drive download directory |
| `KB_DIR` | `~/gws_backup/kb` | AI-readable knowledge base output |
| `SKILL_DIR` | `~/.claude/skills/gws-drive-backup` | Installed skill directory |

## Workflow

1. Run the end-to-end sync script:
   ```bash
   bash ~/.claude/skills/gws-drive-backup/scripts/sync_kb.sh "$BACKUP_DIR" "$KB_DIR"
   ```
   This executes all six phases: metadata export, Drive download, local conversion, verification, KB population, and index generation with PR creation.

2. If you need to run individual phases, see the main skill SKILL.md for per-phase commands.

3. After the PR is merged, team members can access the KB via GitHub MCP tools or by cloning the repository.

## Configuration

Place these files in `$KB_DIR` before running:
- `category_mapping.json` — maps Drive folder paths to KB categories
- `skip_patterns.json` — regex patterns for files to exclude

See `examples/` in the gws-drive-backup repo for templates.

## Safety

This skill only performs read operations on Google Drive. All changes to the KB repository go through pull requests — nothing is pushed directly to main.
