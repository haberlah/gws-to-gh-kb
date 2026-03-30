---
name: kb-update
description: Propose changes to knowledge base documents via pull request
---

# KB Update

Make changes to knowledge base documents and submit them as a pull request for review.

## Workflow

1. **Create a branch** from the KB repository's main branch:
   ```bash
   git checkout -b docs/description-of-change
   ```

2. **Make changes** to the relevant `.md` or `.csv` files in the KB directory. Preserve YAML frontmatter in `.md` files — only edit the body content below the closing `---`.

3. **Regenerate the index** to reflect any metadata changes:
   ```bash
   python3 ~/.claude/skills/gws-drive-backup/scripts/build_index.py "$KB_DIR"
   ```

4. **Commit and push**:
   ```bash
   git add -A
   git commit -m "docs: description of change"
   git push -u origin docs/description-of-change
   ```

5. **Create a pull request**:
   ```bash
   gh pr create --title "docs: description of change" --body "Summary of what changed and why."
   ```

## Rules

- **Never push directly to main.** All changes go through pull requests.
- Preserve YAML frontmatter structure — do not remove or rename frontmatter fields.
- If adding a new document, ensure it has a valid `category` that exists in `category_mapping.json`.
- After the PR is merged, the next `kb-sync` run will reconcile any conflicts with upstream Drive changes.
