# tools

Scripts used to generate and maintain the SVG panels. Run from the repo root.

| Script | Purpose |
|:--|:--|
| `gen_timeline.py` | Builds `timeline.svg` from the role data |
| `gen_lifecycle.py` | Builds `erp-lifecycle.svg` (reuses the theme/defs from `services.svg`) |
| `enhance.py` | Idempotent pass: ERP-first copy and `<title>`/`<desc>` accessibility metadata on every SVG |
| `retheme.py`, `retheme_ios.py`, `polish.py` | Earlier theme and motion passes (kept for reference) |

```bash
python3 tools/gen_lifecycle.py .
python3 tools/enhance.py .
```
