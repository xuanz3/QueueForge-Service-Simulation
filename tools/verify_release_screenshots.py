from __future__ import annotations

import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "docs/assets/readme"
README = ROOT / "README.md"

EXPECTED = [
    "01-product-overview.png",
    "02-scenario-configuration.png",
    "03-live-run-lifecycle.png",
    "04-staffing-comparison.png",
    "05-analytics-json-output.png",
    "06-simulation-kpis.png",
    "07-simulation-json-output.png",
    "08-mobile-interface.png",
]

TIGHT_CROPS = {
    "02-scenario-configuration.png",
    "05-analytics-json-output.png",
    "07-simulation-json-output.png",
}


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"Invalid PNG signature: {path}")
    return struct.unpack(">II", data[16:24])


if not ASSET_DIR.is_dir():
    raise SystemExit("README screenshot directory is missing")

actual = sorted(path.name for path in ASSET_DIR.iterdir() if path.is_file())
if actual != EXPECTED:
    raise SystemExit(
        "README screenshot set must contain exactly eight named PNG files:\n"
        f"expected={EXPECTED}\nactual={actual}"
    )

for name in EXPECTED:
    path = ASSET_DIR / name
    width, height = png_dimensions(path)

    if name == "08-mobile-interface.png":
        if width < 390 or height < 800:
            raise SystemExit(
                f"Mobile screenshot dimensions are too small: {name} {width}x{height}"
            )
    elif name in TIGHT_CROPS:
        if width < 800 or height < 250:
            raise SystemExit(
                f"JSON output screenshot dimensions are too small: "
                f"{name} {width}x{height}"
            )
    elif width < 1200 or height < 800:
        raise SystemExit(
            f"Desktop screenshot dimensions are too small: {name} {width}x{height}"
        )

    minimum_bytes = 10_000 if name in TIGHT_CROPS else 20_000
    if path.stat().st_size < minimum_bytes:
        raise SystemExit(f"Screenshot file is unexpectedly small: {name}")

if not README.is_file():
    raise SystemExit("README.md is missing")

readme = README.read_text(encoding="utf-8")
references = re.findall(
    r'<img\s+[^>]*src="docs/assets/readme/([^"]+\.png)"',
    readme,
)
if references != EXPECTED:
    raise SystemExit(
        "README must reference exactly the eight screenshots in order:\n"
        f"expected={EXPECTED}\nactual={references}"
    )

if readme.count("<img ") != 8:
    raise SystemExit("README contains additional HTML images")

if re.search(r"!\[[^\]]*\]\([^)]+\)", readme):
    raise SystemExit("README contains additional Markdown images")

if 'width="320"' not in readme:
    raise SystemExit("The mobile screenshot is not rendered at a controlled width")

if '<td colspan="2">' not in readme:
    raise SystemExit("The desktop JSON output is not rendered full-width")

print("README screenshot contract passed: exactly 8 product screenshots.")
