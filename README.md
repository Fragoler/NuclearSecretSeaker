# NuclearSS — Secret Seeker for Git Repositories

> Protect repository from leaking tokens, passwords, and other secrets

NuclearSS automatically scans files before every `git commit` and `git push`.  
If no secrets are found — it stays silent and never gets in your way.  
If something is found — an interactive TUI will show the issue and let you resolve it right in the terminal.

---

## Quick Start

### apt (Debian / Ubuntu)
```bash
curl -fsSL https://raw.githubusercontent.com/Fragoler/NuclearSecretSeaker/refs/heads/main/scripts/apt-repo-install.sh | sudo bash
```

### Manual build (no apt)
```bash
curl -fsSL https://raw.githubusercontent.com/Fragoler/NuclearSecretSeaker/refs/heads/main/scripts/build.sh | sudo bash
```

### Connect to a repository
```bash
nuclearss install          # current repository
nuclearss install /path    # specific repository
```

After that, NuclearSS will run automatically on every commit and push.

---

## Commands

| Command | Description                         |
|---|-------------------------------------|
| `nuclearss install [path]` | Install git hooks into a repository |
| `nuclearss check [path]` | One-time scan of a directory        |
| `nuclearss report [path]` | Generate a HTML report              |
| `nuclearss ignore <path>` | Add a path to the exclusion list    |
| `nuclearss tui [file.json]` | Open the interactive results viewer |

---

## How It Works

### Components

**`nuclearss-seaker`** — the scanning engine.  
Recursively walks files, applies regex patterns from `patterns.json` with priorities and danger levels.  
Respects `.gitignore`, the `.nuclearss` config file, and `-x` CLI flags.  
Outputs results as JSON.

**`nuclearss`** — the orchestrator and TUI.  
Runs `nuclearss-seaker` and, if findings are present, opens the terminal interface.  
Lets you add a specific secret or file to the exclusion list — saved to `.nuclearss`.

**`nuclearss-pdf`** — the HTML report generator.  
Takes JSON from `nuclearss-seaker` and produces a report for the security team.

### `.nuclearss` Config

Created automatically by `nuclearss install`. Can also be edited manually:

```
dir:  node_modules        # ignore a directory
dir:  .idea
file: secrets.example.env # ignore a file
text: MY_FAKE_TOKEN_123   # ignore a specific value
```

---

*Built for MEPhI Hackathon 2026. MIT License.*
