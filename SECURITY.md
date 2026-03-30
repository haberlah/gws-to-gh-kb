# Security

## Credential handling

This skill interacts with Google Workspace via the `gws` CLI, which stores OAuth credentials encrypted (AES-256-GCM) at `~/.config/gws/credentials.enc` with the encryption key held in your OS keyring. The skill itself never reads, stores, or transmits credentials directly.

## Write-guard hook

The included `hooks/gws-write-guard.sh` is a Claude Code PreToolUse hook that blocks any `gws` CLI command containing a write verb (`create`, `update`, `delete`, `send`, `trash`, `move`, `copy`, and others). This prevents AI agents from accidentally modifying Google Workspace data. Install it as described in the README.

## Reporting vulnerabilities

If you discover a security issue, please email david@bellamed.ai rather than opening a public issue. I will acknowledge receipt within 48 hours and aim to provide a fix or mitigation within 7 days.

## Scope

This skill performs read-only operations against Google Workspace APIs. It does not:
- Store or transmit Google credentials
- Modify any Google Workspace data (when the write-guard hook is installed)
- Send data to any third-party service
- Require network access beyond the Google API endpoints
