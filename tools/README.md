# tools

Scripts used to generate and maintain the SVG panels. Run from the repo root.

| Script | Purpose |
|:--|:--|
| `gen_timeline.py` | Builds `timeline.svg` from the role data |
| `gen_lifecycle.py` | Builds `erp-lifecycle.svg` (reuses the theme/defs from `services.svg`) |
| `gen_header_contact.py` | **Header + Get in Touch.** Builds `header-identity.svg`, `cta/*`, `nav/*`, `contact-hero.svg`, `contact/*`, `footer-bottom.svg`. Text is drawn as vector outlines (via `svgtext.py`), so no embedded fonts. `python3 tools/gen_header_contact.py .` |
| `svgtext.py` | HarfBuzz + fontTools text-to-path helper used by the generator (fonts in `tools/fonts/`). Needs `pip install fonttools brotli uharfbuzz` |
| `remove_sliding_glow.py` | Strips the travelling border comet and the sliding border gradient from every panel. Idempotent. `python3 tools/remove_sliding_glow.py .` |
| `clean_bg.py` | Removes background effects (aurora blobs, glows, grain/dots, shine sweep). `python3 tools/clean_bg.py SRC DST` |
| `retype_ios.py` | **Typography.** SF Pro stack + embedded Inter fallback, iOS caps/tracking, chip refit. Run last: `python3 tools/retype_ios.py SRC DST` |
| `gen_robot_armor.py` | **Current mascot.** Original armoured "Vanguard" robot (lens eye, pauldrons, thrusters). Run after `gen_robot.py` once, or on its own to regenerate. |
| `gen_robot.py` | Rebuilds the robot mascot in `robot.svg` (breathing, head turn, blink, wave, ground shadow). `python3 tools/gen_robot.py robot.svg` |
| `enhance.py` | Idempotent pass: ERP-first copy and `<title>`/`<desc>` accessibility metadata on every SVG |
| `retheme_warm_ios.py` | **Current theme.** Warm iOS palette (orange/ember/amber), warm neutrals, calmer motion. `python3 tools/retheme_warm_ios.py SRC DST` |
| `retheme.py`, `retheme_ios.py`, `polish.py` | Earlier theme and motion passes (kept for reference) |

Pipeline order for the current look: `retheme_warm_ios.py` -> `gen_robot.py` + `gen_robot_armor.py` (robot only) -> `retype_ios.py` -> `clean_bg.py`.

```bash
pip install fonttools brotli uharfbuzz
python3 tools/gen_header_contact.py .
python3 tools/remove_sliding_glow.py .
python3 tools/gen_lifecycle.py .
python3 tools/enhance.py .
```
