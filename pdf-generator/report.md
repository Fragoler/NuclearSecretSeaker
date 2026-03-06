# Secret Leak Report

**Generated:** Fri Mar  6 20:06:35 MSK 2026

## Summary

- **Total findings:** 3
- **Average risk level:** 168.3/255

## Findings

Hardcoded API key detected in `src/config.py` on line `42`:

<div class="snippet-box" style="background-color: #FF0000; color: #000000;">api_key = "sk-abc123"</div>

Token exposed in script in `scripts/deploy.sh` on line `15`:

<div class="snippet-box" style="background-color: #C83700; color: #000000;">TOKEN="ghp_xxxxx"</div>

Base64 encoded data in `README.md` on line `10`:

<div class="snippet-box" style="background-color: #32CD00; color: #000000;">encoded = "aGVsbG8gd29ybGQ="</div>

---
*Generated automatically. Review findings and take appropriate action.*
