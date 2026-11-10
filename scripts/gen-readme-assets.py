#!/usr/bin/env python3
"""README visuals for dsh-soe-decision-check (docs/assets/), derived from the
shipped code and rule pack.

Outputs (idempotent overwrite):
  docs/assets/dsh-soe-decision-check-hero-{zh,en}-{light,dark}.webp  1440x576 (Pillow)
  docs/assets/dsh-soe-decision-check-flow-v5-{light,dark}.svg        1100x660 (hand SVG)

What the drawings are derived from (read before writing, never invented):

  src/model.ts        COLUMNS maps the register's column aliases onto canonical
                      row fields (matterNo, proposal, basis, consulted,
                      consultedAt, meetingAt, decision, voteResult, category,
                      ...); SPEC.header declares company / body / meetingNo /
                      meetingAt / checkedAt. parseTable() normalises aliases
                      case-insensitively, ignoring spaces, underscores and
                      hyphens; the original file is only ever read.
  src/index.ts        the only tool is `soe_decision_check(file | material)`
                      (with optional rulesFile / only overrides). It resolves
                      the packaged rule pack, parses the material, runs the
                      rules and projects the report through buildView().
  src/model.ts        runCheck() -> runTableCheck(); every finding carries
                      locator.row plus locator.column, found, expected, fix.
  rules/soe-decision-check.yaml
                      8 rules, pack version "2026.1", all kind
                      derived-from-principle (severity capped at warn):
                        SD-001  presenceAny  proposal|basis         (row)
                        SD-002  conditionalPresence consulted -> consultedAt
                        SD-003  date consultedAt not after meetingAt
                        SD-004  presence decision
                        SD-005  conditionalPresence decision -> voteResult
                        SD-006  enum category, values [] -> skipped
                        SD-007  headerPresence company|body         (header)
                        SD-008  unique matterNo                     (cross-row)
                      Loaded through a citation gate: every excerpt must be a
                      verbatim quotation of >= 8 characters, and the kind caps
                      the severity.
  samples/quickstart/ one real run: input SD-001-unsafe.json (row 1 has an
                      empty proposal and basis; SD-006 ships values:[]) ->
                      1 issue (SD-001, warn), 1 skipped (SD-006). The figures
                      quote that run; no count is invented.

Design notes
------------
* Hero: left column is prose (kicker / two-line title / two value lines /
  subtitle / meta / footer). Right column is a register specimen on a card:
  header plus three matter rows, the first row's consultedAt sits after
  meetingAt, and the difference card below carries the exact
  locator/found/expected/fix of SD-003 as printed in README "示例".
* Flow: grammar = THREE-SEGMENT PROCEDURE TRACE BAND. The register and the rule
  pack are two stacked bars feeding one checking core; one matter is then laid
  out as a single continuous trace band split into 会前 / 会议审议 / 决议记录,
  each segment carrying the fields the ledger wrote there and the rule chips
  that read them. The empty proposal/basis are dashed gap marks, and SD-003
  states its cross-segment comparison in its own chip. Deliberately not a row
  of equal nodes with arrows. Two channels leave the band (issues[] /
  skipped[]) into the report; the verdict stays outside the figure.
* Token-only figure (no localized prose), so one light/dark pair serves all
  five README languages; only the hero is localized zh/en.

Every label is measured with the font that draws it (msyh.ttc / msyhbd.ttc /
consola.ttf / segoeui*.ttf); a label that would leave its box aborts the run
instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, and Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf /
           segoeui.ttf / segoeuib.ttf.
"""
from __future__ import annotations

import os
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

HERO_W, HERO_H = 1440, 576
FLOW_W, FLOW_H = 1100, 660

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_EN = r"C:\Windows\Fonts\segoeui.ttf"
FONT_EN_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_EN, FONT_EN_BOLD):
    if not os.path.exists(_p):
        sys.exit(f"FATAL: font missing: {_p}")

# Family accent (#4B67B4 / #8496f5) on the page backgrounds fixed by the task.
SKIN = {
    "light": dict(bg_from="#f9f6fd", bg_to="#e4eaf8", card="#ffffff",
                  zone="#f5f2fc", edge="#e4e0f0", text="#141419",
                  sub="#4d5261", faint="#8f94a4", accent="#4B67B4",
                  green="#15803d", green_pill="#e7f4e9",
                  amber="#b45309", amber_pill="#fdf1e2",
                  amber_tint="#fdf6ea", slate="#64748b",
                  pill="#efeaf9", grid="#e8e4f2", shadow=(30, 24, 62)),
    "dark": dict(bg_from="#131a2a", bg_to="#0c1016", card="#1b2231",
                 zone="#171e2d", edge="#2e374b", text="#f0f3f9",
                 sub="#a8b1c4", faint="#737b8d", accent="#8496f5",
                 green="#57c46b", green_pill="#1d2f22",
                 amber="#fbbf24", amber_pill="#33280f",
                 amber_tint="#241f15", slate="#94a3b8",
                 pill="#242d42", grid="#1e2636", shadow=(0, 0, 0)),
}

_KINDS = {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD, "mono": FONT_MONO,
          "en": FONT_EN, "en_bold": FONT_EN_BOLD}
_MEASURE = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def font(size, kind="cjk_bold"):
    return ImageFont.truetype(_KINDS[kind], size)


def width(text, size, kind):
    return _MEASURE.textlength(text, font=font(size, kind))


def hx(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def ink(skin, key):
    return hx(SKIN[skin][key])


def must_fit(text, size, kind, budget, where):
    got = width(text, size, kind)
    if got > budget:
        sys.exit(f"FATAL: {where}: {text!r} needs {got:.0f}px at {size}px, "
                 f"the box allows {budget:.0f}px. Shorten it or widen the box.")
    return got


# ---------------------------------------------------------------------------
# Pillow primitives
# ---------------------------------------------------------------------------
def gradient(w, h, c1, c2):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.18 * (y / h) + 0.82 * (y / h) ** 1.3
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return img


def glow(img, cx, cy, radius, color, alpha):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 12
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / (steps + 1))),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def shadow_card(img, box, skin, radius=22, spread=26, fill_key="card",
                edge_key="edge", edge_width=2):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(spread, 0, -3):
        sd.rounded_rectangle([x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
                             radius=radius + i // 6,
                             fill=SKIN[skin]["shadow"] + (int(9 * (1 - i / spread)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=ink(skin, fill_key),
                        outline=ink(skin, edge_key), width=edge_width)
    return base.convert("RGB")


def pill(img, xy, text, skin, size=16, kind="cjk_bold", fg="accent",
         bg="pill", padx=16, pady=9):
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    tw = d.textlength(text, font=f)
    x, y = xy
    h = size + pady * 2
    d.rounded_rectangle([x, y, x + tw + padx * 2, y + h], radius=h // 2,
                        fill=ink(skin, bg))
    d.text((x + padx, y + h // 2), text, font=f, fill=ink(skin, fg),
           anchor="lm")
    return x + tw + padx * 2


def tx(d, xy, text, size, kind, color, anchor="ls"):
    d.text(xy, text, font=font(size, kind), fill=color, anchor=anchor)


# ---------------------------------------------------------------------------
# Hero copy (localized zh / en). The SD-003 finding is the example printed in
# README "示例"; the register header is the sample quickstart header.
# ---------------------------------------------------------------------------
HERO = {
    "zh": dict(
        kicker="DSH 核对插件 · 决策留痕",
        title=["三重一大", "台账核对"],
        title_size=88, title_base=196, title_gap=88,
        value=["台账里写了什么，就核对什么——", "缺哪一栏、差在哪天，指到行与栏。"],
        value_size=32, value_base=346, value_gap=42,
        sub="一份台账、八条规则，只列差异，不判合规。",
        meta="soe_decision_check · SD-001…SD-008 · v2026.1",
        foot="dsh-soe-decision-check · Apache-2.0 · DSH ≥0.2.1 <0.3.0",
        sheet="决策台账 · 只读核对",
        sheet_meta="某某集团有限公司 · 党委会 · 2026 年第 3 次",
        cols=["议题", "前置研究日期", "会议日期", "决议结论"],
        rows=[["某某技改项目立项", "2026-03-10", "2026-03-05", "同意立项"],
              ["某某道路改造", "2026-02-20", "2026-03-05", "同意"],
              ["某某设备采购", "2026-01-12", "2026-01-20", "同意"]],
        card_title="差异卡 · 定位到行与栏",
        severity="warn",
        fields=[("locator", "第 1 行 · 字段 consultedAt"),
                ("found", "「consultedAt」2026-03-10 晚于 2026-03-05"),
                ("expected", "不应晚于「meetingAt」的 2026-03-05"),
                ("fix", "核对两个日期的填写")],
        note="issues[] 与 skipped[] 一起读 · 空清单不读作「没问题」",
    ),
    "en": dict(
        kicker="DSH CHECKER · DECISION TRACE",
        title=["SOE decision", "ledger check"],
        title_size=80, title_base=196, title_gap=83,
        value=["Checks what the ledger itself wrote,",
               "and pins each gap to row and field."],
        value_size=30, value_base=342, value_gap=40,
        sub="Eight rules, one ledger — never a verdict.",
        meta="soe_decision_check · SD-001…SD-008 · v2026.1",
        foot="dsh-soe-decision-check · Apache-2.0 · DSH ≥0.2.1 <0.3.0",
        sheet="DECISION REGISTER · READ-ONLY",
        sheet_meta="Example Group Co., Ltd. · Party committee · 3rd session 2026",
        cols=["matter", "consultedAt", "meetingAt", "decision"],
        rows=[["retrofit project", "2026-03-10", "2026-03-05", "approved"],
              ["road upgrade", "2026-02-20", "2026-03-05", "approved"],
              ["equipment buy", "2026-01-12", "2026-01-20", "approved"]],
        card_title="Difference card · row and field",
        severity="warn",
        fields=[("locator", "row 1 · field consultedAt"),
                ("found", "consultedAt 2026-03-10 is after meetingAt 2026-03-05"),
                ("expected", "consultedAt must not fall after 2026-03-05"),
                ("fix", "check which of the two dates is wrong")],
        note="read issues[] and skipped[] together · an empty list is not a pass",
    ),
}


def hero(lang, skin):
    zh = lang == "zh"
    s = SKIN[skin]
    H = HERO[lang]
    img = gradient(HERO_W, HERO_H, s["bg_from"], s["bg_to"])
    img = glow(img, 1200, 36, 380, ink(skin, "accent"),
               24 if skin == "light" else 38)
    img = glow(img, 120, 548, 250, ink(skin, "green"),
               8 if skin == "light" else 12)

    # ---- left column: kicker / title / two value lines / sub / meta / foot --
    m, colw = 60, 588
    kick_kind = "cjk_bold" if zh else "en_bold"
    must_fit(H["kicker"], 16, kick_kind, colw - 60, "hero kicker")
    pill(img, (m, 52), H["kicker"], skin, size=16, kind=kick_kind,
         padx=17, pady=9)

    d = ImageDraw.Draw(img)
    tkind = "cjk_bold" if zh else "en_bold"
    tsize = H["title_size"]
    for i, line in enumerate(H["title"]):
        must_fit(line, tsize, tkind, colw, f"hero title line {i + 1}")
        d.text((m - 3, H["title_base"] + i * H["title_gap"]), line,
               font=font(tsize, tkind), fill=ink(skin, "text"), anchor="ls")

    vkind = "cjk_bold" if zh else "en_bold"
    for i, line in enumerate(H["value"]):
        must_fit(line, H["value_size"], vkind, colw, f"hero value {i + 1}")
        d.text((m, H["value_base"] + i * H["value_gap"]), line,
               font=font(H["value_size"], vkind), fill=ink(skin, "text"),
               anchor="ls")

    sub_kind = "cjk" if zh else "en"
    must_fit(H["sub"], 26, sub_kind, colw, "hero subtitle")
    tx(d, (m, 434), H["sub"], 26, sub_kind, ink(skin, "sub"))

    must_fit(H["meta"], 20, "mono", colw, "hero meta")
    tx(d, (m, 472), H["meta"], 20, "mono", ink(skin, "faint"))

    d.line([m, 496, m + colw, 496], fill=ink(skin, "grid"), width=2)
    must_fit(H["foot"], 17, "en", colw, "hero footer")
    tx(d, (m, 520), H["foot"], 17, "en", ink(skin, "faint"))

    # ---- right column: the register specimen + the SD-003 difference card --
    px0, py0, px1, py1 = 660, 46, 1384, 530
    img = shadow_card(img, (px0, py0, px1, py1), skin, radius=22)
    d = ImageDraw.Draw(img)
    ix0, ix1 = px0 + 26, px1 - 26

    sheet_kind = "cjk_bold" if zh else "mono"
    must_fit(H["sheet"], 13, sheet_kind, ix1 - ix0 - 150, "hero sheet label")
    tx(d, (ix0, 84), H["sheet"], 13, sheet_kind, ink(skin, "accent"))
    sw = width(H["severity"], 11.5, "mono") + 30
    d.rounded_rectangle([ix1 - sw, 66, ix1, 90], radius=12,
                        fill=ink(skin, "amber_pill"))
    tx(d, (ix1 - sw / 2, 78), H["severity"], 11.5, "mono", ink(skin, "amber"),
       anchor="mm")

    must_fit(H["sheet_meta"], 12.5, "cjk" if zh else "en", ix1 - ix0,
             "hero sheet meta")
    tx(d, (ix0, 108), H["sheet_meta"], 12.5, "cjk" if zh else "en",
       ink(skin, "faint"))

    # table header
    d.rounded_rectangle([ix0, 122, ix1, 152], radius=10, fill=ink(skin, "zone"))
    colx = [ix0 + 14, ix0 + 268, ix0 + 408, ix0 + 530]
    colw_ = [248, 136, 118, ix1 - (ix0 + 530) - 16]
    for i, name in enumerate(H["cols"]):
        kind = "cjk" if zh else "mono"
        must_fit(name, 12, kind, colw_[i] - 12, f"hero col {i}")
        tx(d, (colx[i], 142), name, 12, kind, ink(skin, "faint"))

    # three matter rows; row 1 is the flagged one
    row_h = 46
    for r, row in enumerate(H["rows"]):
        top = 152 + r * row_h
        if r == 0:
            d.rounded_rectangle([ix0, top, ix1, top + row_h], radius=8,
                                fill=ink(skin, "amber_tint"))
            d.rounded_rectangle([ix0, top + 6, ix0 + 4, top + row_h - 6],
                                radius=2, fill=ink(skin, "amber"))
        base = top + 29
        kind0 = "cjk" if zh else "en"
        must_fit(row[0], 13.5, kind0, colw_[0], f"hero row {r} matter")
        tx(d, (colx[0], base), row[0], 13.5, kind0, ink(skin, "text"))
        for c in (1, 2):
            must_fit(row[c], 13, "mono", colw_[c], f"hero row {r} date {c}")
            tx(d, (colx[c], base), row[c], 13, "mono",
               ink(skin, "amber") if (r == 0 and c == 1) else ink(skin, "text"))
        must_fit(row[3], 13, kind0, colw_[3] - 62, f"hero row {r} decision")
        tx(d, (colx[3], base), row[3], 13, kind0, ink(skin, "sub"))

    # SD-003 flag pill on the flagged row
    tag = "SD-003"
    tw = width(tag, 11, "mono")
    d.rounded_rectangle([ix1 - tw - 30, 164, ix1 - 8, 186], radius=11,
                        fill=ink(skin, "amber_pill"))
    tx(d, (ix1 - 19 - tw / 2, 175), tag, 11, "mono", ink(skin, "amber"),
       anchor="mm")

    # difference card
    cy0, cy1 = 312, 512
    d.rounded_rectangle([ix0, cy0, ix1, cy1], radius=18,
                        fill=ink(skin, "zone"), outline=ink(skin, "edge"),
                        width=1)
    d.rounded_rectangle([ix0 + 18, cy0 + 20, ix0 + 22, cy0 + 44], radius=2,
                        fill=ink(skin, "accent"))
    must_fit(H["card_title"], 14, "cjk_bold" if zh else "en_bold",
             ix1 - ix0 - 170, "hero card title")
    tx(d, (ix0 + 32, cy0 + 38), H["card_title"], 14,
       "cjk_bold" if zh else "en_bold", ink(skin, "accent"))
    fw = width("expected", 12, "mono") + 22
    for i, (label, value) in enumerate(H["fields"]):
        y = cy0 + 70 + i * 26
        color = ink(skin, "amber") if label == "found" else ink(skin, "faint")
        tx(d, (ix0 + 32, y), label, 12, "mono", color)
        vkind = "mono" if value.isascii() else ("cjk" if zh else "en")
        must_fit(value, 13.5, vkind, ix1 - (ix0 + 32 + fw) - 18,
                 f"hero field {label}")
        tx(d, (ix0 + 32 + fw, y), value, 13.5, vkind, ink(skin, "text"))

    d.line([ix0 + 32, cy0 + 168, ix1 - 18, cy0 + 168],
           fill=ink(skin, "grid"), width=1)
    must_fit(H["note"], 12, "cjk" if zh else "en", ix1 - ix0 - 60,
             "hero note")
    tx(d, (ix0 + 32, cy0 + 186), H["note"], 12, "cjk" if zh else "en",
       ink(skin, "faint"))

    return img


# ---------------------------------------------------------------------------
# Flow figure — three-segment procedure trace band
# ---------------------------------------------------------------------------
MONO = "'Consolas','SFMono-Regular',Menlo,ui-monospace,monospace"
CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
       "'Source Han Sans SC',sans-serif")


def svg_text(x, y, text, size, kind, color, anchor="start", bold=False,
             budget=None, tag=""):
    if budget is not None:
        must_fit(text, size, kind, budget, tag or text)
    fam = MONO if kind == "mono" else CJK
    weight = ' font-weight="700"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" '
            f'font-family="{fam}" font-size="{size}"{weight} '
            f'text-anchor="{anchor}">{escape(text)}</text>')


def trace_svg(skin):
    s = SKIN[skin]
    accent = s["accent"]
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{FLOW_W}" '
             f'height="{FLOW_H}" viewBox="0 0 {FLOW_W} {FLOW_H}" role="img" '
             f'aria-labelledby="fig-title fig-desc">')
    p.append('<title id="fig-title">dsh-soe-decision-check structure: a '
             'three-segment procedure trace band</title>')
    p.append('<desc id="fig-desc">Register and rule pack feed '
             'runTableCheck(); one matter is drawn as a trace band split into '
             'pre-study, meeting review and resolution record; SD-001 hits the '
             'empty proposal and basis, SD-003 compares the two dates across '
             'the segment boundary, SD-006 is skipped; issues[] and skipped[] '
             'leave the band and the verdict stays with the reviewer.</desc>')
    p.append('<defs>')
    p.append(f'<linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">'
             f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
             f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    p.append('<filter id="soft" x="-25%" y="-25%" width="150%" height="160%">'
             '<feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#16122c" '
             'flood-opacity="0.10"/></filter>')
    p.append('</defs>')
    p.append(f'<rect width="{FLOW_W}" height="{FLOW_H}" fill="url(#bg)"/>')

    # ---- header -----------------------------------------------------------
    p.append(svg_text(44, 58, "dsh-soe-decision-check", 26, "mono",
                      s["text"], bold=True))
    p.append(svg_text(44, 86,
                      "八条规则只读一份「三重一大」决策台账：栏名先归一，再逐段核对程序留痕，差异落到行号与栏名。",
                      13.5, "cjk", s["sub"], budget=1012, tag="subtitle"))
    head = "规则包 v2026.1 · SD-001…SD-008"
    hw = width(head, 11.5, "cjk") + 26
    p.append(f'<rect x="{1056 - hw:.1f}" y="38" width="{hw:.1f}" height="26" '
             f'rx="13" fill="{s["pill"]}"/>')
    p.append(svg_text(1056 - hw + 13, 55.4, head, 11.5, "cjk", accent))

    # ---- bar 1: the register (first input) --------------------------------
    p.append(f'<rect x="44" y="104" width="1012" height="102" rx="18" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" stroke-width="1.5" '
             f'filter="url(#soft)"/>')
    p.append(svg_text(62, 128, "输入 · 决策台账（表头 + rows[]，JSON / YAML，只读）",
                      13.5, "cjk", accent, bold=True, budget=560,
                      tag="input label"))
    tool = "soe_decision_check(file | material)"
    tw = width(tool, 11, "mono") + 24
    p.append(f'<rect x="{1038 - tw:.1f}" y="112" width="{tw:.1f}" height="24" '
             f'rx="12" fill="{s["pill"]}"/>')
    p.append(svg_text(1038 - tw + 12, 128.4, tool, 11, "mono", accent))
    p.append(svg_text(62, 152,
                      "某某集团有限公司 · 党委会 · 2026 年第 3 次 · 会议日期 2026-03-05",
                      11.5, "cjk", s["sub"], budget=520, tag="header values"))
    chip = "SD-007 表头声明 ✓"
    cw = width(chip, 11, "cjk") + 24
    p.append(f'<rect x="{1038 - cw:.1f}" y="138" width="{cw:.1f}" height="22" '
             f'rx="11" fill="{s["green_pill"]}"/>')
    p.append(svg_text(1038 - cw + 12, 153.4, chip, 11, "cjk", s["green"]))
    p.append(f'<rect x="62" y="164" width="976" height="34" rx="10" '
             f'fill="{s["zone"]}"/>')
    cols = ["序号", "议题内容", "决策依据", "前置研究", "前置研究日期",
            "会议日期", "决议结论", "表决结果", "事项类别"]
    p.append(svg_text(76, 186, "rows[]", 11, "mono", accent))
    x = 128.0
    for i, name in enumerate(cols):
        if i:
            p.append(svg_text(x, 186, "·", 11, "cjk", s["faint"]))
            x += 9
        p.append(svg_text(x, 186, name, 11, "cjk", s["text"]))
        x += width(name, 11, "cjk") + 8
    alias = "栏名归一：忽略大小写 / 空格 / 下划线 / 连字符"
    aw = width(alias, 11, "cjk")
    if x + 26 + aw > 1026:
        sys.exit("FATAL: input column tokens collide with the alias note")
    p.append(svg_text(1026, 186, alias, 11, "cjk", s["faint"], anchor="end"))

    # ---- bar 2: the rule pack (second input) ------------------------------
    p.append(f'<rect x="44" y="214" width="1012" height="66" rx="18" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" stroke-width="1.5" '
             f'filter="url(#soft)"/>')
    p.append(svg_text(62, 240, "规则包 · rules/soe-decision-check.yaml", 13.5,
                      "cjk", accent, bold=True, budget=430, tag="rules label"))
    p.append(svg_text(1038, 240, "8 条规则 · 数据不是代码", 11.5, "cjk",
                      s["sub"], anchor="end"))
    p.append(svg_text(62, 264,
                      "加载期校验：excerpt 须为逐字引文且 ≥8 字 · 依据类型封顶（8 条全部 "
                      "derived-from-principle → ≤ warn）· 引文回查 rules/evidence/",
                      11.5, "cjk", s["sub"], budget=790, tag="rules gate"))
    p.append(svg_text(1038, 264, "替换 YAML 即换规则集", 11, "cjk", s["faint"],
                      anchor="end"))

    # ---- the trace band ---------------------------------------------------
    p.append(f'<rect x="44" y="292" width="1012" height="224" rx="18" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" stroke-width="1.5" '
             f'filter="url(#soft)"/>')
    p.append(svg_text(62, 316, "parseMaterial() + loadRulesetFile() → runTableCheck()",
                      12, "mono", accent, budget=430, tag="core label"))
    p.append(svg_text(1038, 316,
                      "命中进 issues[] · 未执行进 skipped[] · 跑过未命中两栏都不进",
                      11, "cjk", s["faint"], anchor="end"))
    # matter row strip
    p.append(f'<rect x="62" y="326" width="976" height="40" rx="10" '
             f'fill="{s["zone"]}"/>')
    p.append(svg_text(76, 351, "第 1 行 · 某某技改项目立项", 13, "cjk",
                      s["text"], bold=True, budget=200, tag="row title"))
    p.append(svg_text(290, 351, "序号 1", 11.5, "cjk", s["sub"]))
    p.append(svg_text(350, 351, "涉及金额 4800 万元", 11.5, "cjk", s["sub"]))
    uq = "SD-008 跨行唯一 ✓"
    uw = width(uq, 11, "cjk") + 24
    p.append(f'<rect x="{1030 - uw:.1f}" y="335" width="{uw:.1f}" height="22" '
             f'rx="11" fill="{s["green_pill"]}"/>')
    p.append(svg_text(1030 - uw + 12, 350.4, uq, 11, "cjk", s["green"]))

    # trace rail: three stations
    seg_l, seg_r = 62.0, 1038.0
    seg_w = (seg_r - seg_l) / 3
    seg_x = [seg_l + i * seg_w for i in range(4)]
    rail_y = 380.0
    p.append(f'<line x1="{seg_l + 18}" y1="{rail_y}" x2="{seg_r - 24}" '
             f'y2="{rail_y}" stroke="{accent}" stroke-width="2" '
             f'stroke-linecap="round"/>')
    p.append(f'<path d="M{seg_r - 32} {rail_y - 5}l8 5-8 5" fill="none" '
             f'stroke="{accent}" stroke-width="2" stroke-linecap="round" '
             f'stroke-linejoin="round"/>')
    for i in range(3):
        cx = seg_x[i] + seg_w / 2
        p.append(f'<circle cx="{cx:.1f}" cy="{rail_y}" r="10" '
                 f'fill="{s["card"]}" stroke="{accent}" stroke-width="1.6"/>')
        p.append(svg_text(cx, rail_y + 3.8, str(i + 1), 11, "mono", accent,
                          anchor="middle"))
    for i in (1, 2):
        p.append(f'<line x1="{seg_x[i]:.1f}" y1="392" x2="{seg_x[i]:.1f}" '
                 f'y2="494" stroke="{s["edge"]}" stroke-width="1.2" '
                 f'stroke-dasharray="4 5"/>')

    # three segments: fields + rule chips
    seg_titles = ["会前 · 议题与前置研究", "会议审议", "决议记录"]
    lines = [
        [[("前置研究日期", "2026-02-20", None)],
         [("前置研究", "是", None)],
         [("议题内容", "空", "gap"), ("决策依据", "空", "gap")]],
        [[("会议日期", "2026-03-05", None)],
         [("事项类别", "重大项目安排", None)],
         [("条款（九）", "以会议形式决策", None)]],
        [[("决议结论", "同意立项，概算 ≤4800 万元", None)],
         [("表决结果", "应到 9 · 实到 9 · 同意 9", None)],
         [("承办部门", "发展策划部", None)]],
    ]
    for i in range(3):
        sx = seg_x[i] + 16
        p.append(svg_text(sx, 406, seg_titles[i], 13.5, "cjk", accent,
                          bold=True, budget=seg_w - 32, tag=f"seg {i} title"))
        inner = seg_w - 34
        for row_i, tokens in enumerate(lines[i]):
            y = 424 + row_i * 19
            gx = sx
            for label, value, tone in tokens:
                lw = width(label, 11.5, "cjk")
                p.append(svg_text(gx, y, label, 11.5, "cjk", s["sub"]))
                if tone == "gap":
                    pw = 34
                    p.append(f'<rect x="{gx + lw + 7:.1f}" y="{y - 12}" '
                             f'width="{pw}" height="17" rx="8.5" fill="none" '
                             f'stroke="{s["amber"]}" stroke-width="1.2" '
                             f'stroke-dasharray="3 3"/>')
                    p.append(svg_text(gx + lw + 7 + pw / 2, y - 0.2, value, 11,
                                      "cjk", s["amber"], anchor="middle"))
                    gx += lw + 7 + pw + 20
                else:
                    must_fit(value, 12, "cjk", inner - (gx - sx) - lw - 8,
                             f"seg {i} {label}")
                    p.append(svg_text(gx + lw + 8, y, value, 12, "cjk",
                                      s["text"]))
                    gx += lw + 8 + width(value, 12, "cjk") + 18

    chips = [
        [("SD-001 命中", "amber"), ("SD-002 通过", "green")],
        [("SD-003 02-20 ≤ 03-05 ✓", "green"), ("SD-006 skipped", "skip")],
        [("SD-004 通过", "green"), ("SD-005 通过", "green")],
    ]
    for i in range(3):
        cx = seg_x[i] + 16
        for text, tone in chips[i]:
            fg = {"amber": s["amber"], "green": s["green"],
                  "skip": s["slate"]}[tone]
            bg = {"amber": s["amber_pill"], "green": s["green_pill"],
                  "skip": s["zone"]}[tone]
            tw = width(text, 11, "cjk") + 22
            outline = (f' stroke="{s["slate"]}" stroke-width="1" '
                       f'stroke-dasharray="3 3"' if tone == "skip" else "")
            p.append(f'<rect x="{cx:.1f}" y="478" width="{tw:.1f}" '
                     f'height="22" rx="11" fill="{bg}"{outline}/>')
            p.append(svg_text(cx + tw / 2, 493.4, text, 11, "cjk", fg,
                              anchor="middle"))
            cx += tw + 10
        if cx - 16 > seg_x[i] + seg_w - 22:
            sys.exit(f"FATAL: segment {i} rule chips overflow their column")

    # ---- outputs ----------------------------------------------------------
    p.append(f'<rect x="44" y="524" width="656" height="78" rx="18" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" stroke-width="1.5" '
             f'filter="url(#soft)"/>')
    p.append(svg_text(62, 548, "issues[] · 1 条", 13.5, "cjk", accent,
                      bold=True))
    sev = "warn 1"
    sw = width(sev, 11, "mono") + 24
    p.append(f'<rect x="{682 - sw:.1f}" y="530" width="{sw:.1f}" height="22" '
             f'rx="11" fill="{s["amber_pill"]}"/>')
    p.append(svg_text(682 - sw + 12, 545.4, sev, 11, "mono", s["amber"]))
    p.append(svg_text(62, 570, "SD-001 · 第 1 行 · 字段 proposal", 11, "cjk",
                      s["sub"]))
    p.append(svg_text(62, 590,
                      "proposal、basis 都为空 → 补填议题内容与决策依据",
                      11.5, "cjk", s["text"], budget=620, tag="issue line"))

    p.append(f'<rect x="716" y="524" width="340" height="78" rx="18" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" stroke-width="1.5" '
             f'filter="url(#soft)"/>')
    p.append(svg_text(734, 548, "skipped[] · 1 条", 13.5, "cjk", s["sub"],
                      bold=True))
    p.append(f'<rect x="{1030 - 74:.1f}" y="530" width="74" height="22" '
             f'rx="11" fill="{s["zone"]}" stroke="{s["slate"]}" '
             f'stroke-width="1" stroke-dasharray="3 3"/>')
    p.append(svg_text(1030 - 37, 545.4, "SD-006", 11, "mono", s["slate"],
                      anchor="middle"))
    p.append(svg_text(734, 570, "values 未配置 · 规则库不硬编码", 11, "cjk",
                      s["faint"], budget=306, tag="skip reason"))
    p.append(svg_text(734, 590, "「category」口径由本机构规定",
                      11.5, "cjk", s["text"], budget=306, tag="skip line"))

    # ---- footer -----------------------------------------------------------
    p.append(f'<line x1="44" y1="612" x2="1056" y2="612" stroke="{s["edge"]}" '
             f'stroke-width="1"/>')
    p.append(svg_text(44, 632,
                      "报告：error 0 · warn 1 · info 0 ｜ issueCount 1 · "
                      "skippedCount 1 ｜ markdown + reportJson ｜ 结论留给复核人",
                      11, "cjk", s["sub"], budget=1012, tag="footer 1"))
    p.append(svg_text(44, 650,
                      "只读材料 · 无网络 · 不调用模型 · 原件不改 ｜ "
                      "config：rulesFile · disabledRules · onlyRules · "
                      "skipNotes · timeoutMs",
                      11, "cjk", s["faint"], budget=1012, tag="footer 2"))
    p.append('</svg>')
    return "\n".join(p) + "\n"


def main():
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            img = hero(lang, skin)
            path = os.path.join(OUT, f"dsh-soe-decision-check-hero-{lang}-{skin}.webp")
            img.save(path, format="WEBP", quality=90, method=6)
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"dsh-soe-decision-check-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(trace_svg(skin))
    print("wrote 4 hero webp + 2 flow-v5 svg to docs/assets/ "
          "(hero localized zh/en; the trace band is token-only and shared)")


if __name__ == "__main__":
    main()
