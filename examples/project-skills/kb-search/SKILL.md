---
name: kb-search
description: Search the knowledge base by category, tag, or keyword
---

# KB Search

Search the AI-readable knowledge base using the master index or full-text search.

## How to search

### By index (structured queries)

Parse `index.json` in the KB root directory. Each entry contains:

| Field | Description |
|-------|-------------|
| `title` | Document title |
| `category` | Topic directory (e.g. architecture, strategy) |
| `tags` | Auto-generated tags from content |
| `doc_type` | Document type (e.g. policy, guide, meeting-notes) |
| `sensitivity` | Sensitivity label (public, internal, confidential) |
| `last_modified` | Last modification date from Google Drive |
| `path` | Relative path to the .md or .csv file |

Filter `index.json` with `jq`:

```bash
# All documents in a category
jq '[.[] | select(.category == "architecture")]' index.json

# Documents modified in the last 30 days
jq '[.[] | select(.last_modified > "2026-03-01")]' index.json

# Documents with a specific tag
jq '[.[] | select(.tags | index("security"))]' index.json

# Confidential documents only
jq '[.[] | select(.sensitivity == "confidential")]' index.json
```

### By content (full-text search)

Use `grep` for local searches:

```bash
grep -rl "search term" "$KB_DIR"
```

Or use GitHub MCP `search_code` if the KB is hosted in a GitHub repository.

## Notes

- Available categories depend on your `category_mapping.json` configuration
- The index is regenerated each time `sync_kb.sh` runs
- Sensitivity labels are derived from folder paths and document content during KB population
