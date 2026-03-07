# NuclearSecretSeaker

 NuclearSS: The Utility that protects the git repository from leaks of tokens, passwords, secrets, and other confidential information.

### How to build:

if using **apt** - see the [apt-repo-install.sh](scripts/apt-repo-install.sh).

One cmd installation:
```
curl -fsSL https://raw.githubusercontent.com/Fragoler/NuclearSecretSeaker/refs/heads/main/apt-repo-install.sh | sudo bash
```


if **not** using apt then via script - see the [build.sh](scripts/build.sh).

One cmd installation:
```
curl -fsSL https://raw.githubusercontent.com/Fragoler/NuclearSecretSeaker/refs/heads/main/build.sh | sudo bash
```


### How to use:

```
nuclearss check /path    # Run default check /path directory
nuclearss report /path   # Generate PDF report for path
nuclearss tui data.json  # Launch TUI with JSON file
nuclearss install /path  # Install git hooks for selected repository
nuclearss install        # Install git hooks for current repository
nuclearss ignore /path   # Ignore all secrets in the specified path
```


Was made for MEPhI hackaton 2026.
