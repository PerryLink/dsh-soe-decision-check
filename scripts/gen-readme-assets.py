#!/usr/bin/env python3
"""Generate the README hero assets for dsh-soe-decision-check.

Outputs (idempotent overwrite):
  docs/assets/dsh-soe-decision-check-flow-light.svg
  docs/assets/dsh-soe-decision-check-flow-dark.svg
      Hero workflow diagram, one hand-written SVG per colour scheme. Text
      inside is command-surface tokens only (`soe_decision_check`,
      `rules/*.yaml`, `SD-001 … SD-008`, `findings[]`, `skipped[]`,
      `rules/evidence/`), so all five README languages share the same pair.

No raster asset is emitted: this repository publishes no benchmark or
measured-results file, so the playbook's evidence bar chart (webp, quality 90)
does not apply here. Add it only when a real `benchmark/RESULTS.md` exists —
never invent data for a picture.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges use labelColor #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e"),
}

# --- font probe: the family template refuses to ship tofu boxes ------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to ship an asset "
             "whose text could render as tofu boxes; install one of the "
             "probed fonts and re-run.")


def measure(text: str, size: int) -> float:
    """Width in px of `text` under the probed font, used to fail loud on
    label overflow before an SVG with clipped text is written."""
    return ImageFont.truetype(FONT_PATH, size).getlength(text)


def fit(label: str, size: int, limit: int, where: str) -> None:
    width = measure(label, size)
    if width > limit:
        sys.exit(f"FATAL: {where} label {label!r} is {width:.0f}px wide, "
                 f"over the {limit}px box; shorten it or raise the box size.")


# ---------------------------------------------------------------------------
# Hero workflow SVG (light + dark)
# ---------------------------------------------------------------------------
FLOW_NODES = [
    ("material", "file · material"),
    ("soe_decision_check", "JSON/YAML in"),
    ("rules/*.yaml", "SD-001 … SD-008"),
    ("report", "findings · skipped"),
    ("rules/evidence/", "excerpt ↦ clause"),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 400
    nw, nh, gap = 180, 96, 45
    y0 = 150
    for label, sub in FLOW_NODES:
        fit(label, 16, nw - 16, "node")
        fit(sub, 12, nw - 16, "node sub")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-soe-decision-check workflow">',
        f'<title>dsh-soe-decision-check workflow</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">'
        f'dsh-soe-decision-check</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">decision register · rule pack · '
        f'findings</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    for i, (label, sub) in enumerate(FLOW_NODES):
        x = 60 + i * (nw + gap)
        accent = GREEN[skin] if i == 3 else (FAMILY if i == 1 else s["border"])
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 40}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="16" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 68}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{sub}</text>')
        if i < len(FLOW_NODES) - 1:
            ax = x + nw + 6
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    # citation-gate bar under the rule pack and the report
    bx, bw, by, bh = 285, 630, 285, 52
    for cx in (600, 825):  # rule-pack node centre, report node centre
        parts.append(
            f'<path d="M{cx} {y0 + nh}v{by - y0 - nh}" '
            f'stroke="{FAMILY}" stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" '
        f'fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2"/>')
    parts.append(
        f'<text x="{bx + bw // 2}" y="{by + 33}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="14">citation gate · excerpt must be a verbatim '
        f'quotation · kind ≤ warn</text>')
    parts.append(
        f'<text x="60" y="378" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">inject: [\'tools\'] · no network · no '
        f'model call · the original file is never modified</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"dsh-soe-decision-check-flow-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG hero assets to docs/assets/ "
          "(no evidence chart: this repo publishes no benchmark data)")


if __name__ == "__main__":
    main()
