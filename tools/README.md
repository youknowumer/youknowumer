# tools

Scripts used to generate and maintain the SVG panels. Run from the repo root.

| Script | Purpose |
|:--|:--|
| `gen_timeline.py` | Builds `timeline.svg` from the role data |
| `gen_lifecycle.py` | Builds `erp-lifecycle.svg` (reuses the theme/defs from `services.svg`) |
| `gen_robot_armor.py` | **Current mascot.** Original armoured "Vanguard" robot (lens eye, pauldrons, thrusters). Run after `gen_robot.py` once, or on its own to regenerate. |
| `gen_robot.py` | Rebuilds the robot mascot in `robot.svg` (breathing, head turn, blink, wave, ground shadow). `python3 tools/gen_robot.py robot.svg` |
| `enhance.py` | Idempotent pass: ERP-first copy and `<title>`/`<desc>` accessibility metadata on every SVG |
| `retheme_warm_ios.py` | **Current theme.** Warm iOS palette (orange/ember/amber), warm neutrals, calmer motion. `python3 tools/retheme_warm_ios.py SRC DST` |
| `retheme.py`, `retheme_ios.py`, `polish.py` | Earlier theme and motion passes (kept for reference) |

```bash
python3 tools/gen_lifecycle.py .
python3 tools/enhance.py .
```
