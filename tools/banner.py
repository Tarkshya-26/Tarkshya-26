#!/usr/bin/env python3
"""
Generates assets/banner-{dark,light}.svg — the profile hero, in both GitHub themes.

A terminal window. Left: the identity block, with a role line that types itself
out and cycles. Right: a live system diagram — packets flow USER → AGENT → GATE
→ tools, and every so often one gets refused at the gate.

Edit THEME to retheme, PHRASES/LINES/SPEC to change content, then run
`python3 tools/banner.py` from the repo root.

Notes on why things are built the way they are:

* The diagram is real SVG geometry, not box-drawing characters — JetBrains Mono
  ships no U+2500 block, so an ASCII diagram falls back to whatever mono font the
  viewer has and the rules stop meeting the boxes.
* Typing is a clip rect scaled in `steps()`, which is the one approach that holds
  up in an SVG served as an image. Packet travel is SMIL `animateMotion`, which
  has the widest support of anything that moves along a path.
* Fonts are subset to only the glyphs drawn (~9 KB) and inlined as data URIs;
  GitHub blocks external font loads inside an SVG image. Both are SIL OFL 1.1.
* Everything that moves is disabled under prefers-reduced-motion, which resolves
  to the fully-typed final state rather than to a blank line.
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets"

W, H = 1200, 460
SPLIT = 548                      # x of the divider
CX = 880                         # diagram centre line

THEME = {
    "dark": dict(
        bg="#070a11", panel="#0b0f18", bar="#0e1320", line="#1c2740",
        ink="#e7edf7", muted="#93a1b8", dim="#5a6883", accent="#4d9fff",
        node="#0e1523", grid="rgba(120,150,200,0.05)", threat="#ff5c5c",
    ),
    "light": dict(
        bg="#f4f6fa", panel="#ffffff", bar="#eef1f7", line="#d8e0ee",
        ink="#0d1520", muted="#48566d", dim="#7b89a0", accent="#1f6feb",
        node="#f7f9fd", grid="rgba(30,50,90,0.05)", threat="#d92d20",
    ),
}

TITLE = "tarkshya@github  —  ~/profile"
EYEBROW = "AI & SECURITY ENGINEER"
NAME = ["TARKSHYA", "BHARDWAJ"]

# The role line types itself out, holds, deletes, and moves to the next.
PHRASES = [
    "LLM Engineering",
    "Agentic AI Systems",
    "AI Security",
    "MCP · Tool Boundaries",
]

LINES = [
    ("Giving an agent API access is", "muted"),
    ("giving it execution privilege.", "ink"),
]
FACTS = [
    "NIT SRINAGAR  ·  B.TECH IT  ·  2024—2028",
    "PAYU  ·  INFORMATION SECURITY  ·  2025—2026",
]

LEAVES = ["JIRA", "RISK", "APIs"]
CAPTION = "every call authenticated, scoped, audited — or refused"

TYPE_SIZE = 15
CHAR_W = TYPE_SIZE * 0.6         # JetBrains Mono advance is 0.6em
CYCLE = len(PHRASES) * 4         # seconds; 4s per phrase


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def charset():
    s = TITLE + EYEBROW + CAPTION + "".join(NAME) + "".join(PHRASES)
    s += "".join(LEAVES) + "SYS_ARCH LIVE USER AGENT AUTH GATE refused $"
    s += "".join(t for t, _ in LINES) + "".join(FACTS)
    return "".join(sorted(set(s) - {"\n"}))


def kf(name, stops):
    """Assemble a @keyframes rule from (percent, {prop: value}, timing) stops.

    Every stop carries the timing function for the segment it opens — leaving it
    off any one of them silently drops that segment back to the animation's
    default easing, which is what desynchronises a caret from its clip.
    """
    body = ""
    for pct, props, timing in stops:
        decl = ";".join(f"{k}:{v}" for k, v in props.items())
        if timing:
            decl += f";animation-timing-function:{timing}"
        body += f"{pct:.6g}%{{{decl}}}"
    return f"@keyframes {name}{{{body}}}"


def type_keyframes():
    """Per phrase: a caret+mask group that slides right in character steps, and a
    visibility track that hard-switches at the slot edges.

    The caret and the mask that hides the untyped remainder are siblings under a
    single transform, so they cannot drift apart. An earlier version animated the
    caret separately from a clip path and the two desynchronised.
    """
    css = []
    slot = 100 / len(PHRASES)
    for i, phrase in enumerate(PHRASES):
        n = len(phrase)
        w = round(n * CHAR_W, 1)
        a = i * slot
        typed, held, gone = a + 8, a + 20, a + 23
        step = f"steps({n},end)"

        stops = []
        if a > 0:
            stops.append((0, {"transform": "translateX(0)"}, "linear"))
        stops += [
            (a,     {"transform": "translateX(0)"}, step),
            (typed, {"transform": f"translateX({w}px)"}, "linear"),
            (held,  {"transform": f"translateX({w}px)"}, step),
            (gone,  {"transform": "translateX(0)"}, "linear"),
        ]
        if gone < 100:
            stops.append((100, {"transform": "translateX(0)"}, None))
        css.append(kf(f"cur{i}", stops))

        hold = "steps(1,end)"
        vis = [(0, {"opacity": "1" if a == 0 else "0"}, hold)]
        if a > 0:
            vis += [(a, {"opacity": "0"}, hold), (a + 0.01, {"opacity": "1"}, hold)]
        vis += [(gone, {"opacity": "1"}, hold),
                (gone + 0.01, {"opacity": "0"}, hold),
                (100, {"opacity": "0"}, None)]
        css.append(kf(f"vis{i}", vis))
    return css


def box(o, x, y, w, h, label, p, size=11.5, weight="400", stroke=None):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
             f'fill="{p["node"]}" stroke="{stroke or p["line"]}"/>')
    o.append(f'<text x="{x + w/2}" y="{y + h/2 + 4}" class="m" fill="{p["ink"]}" '
             f'font-size="{size}" font-weight="{weight}" letter-spacing="1.1" '
             f'text-anchor="middle">{esc(label)}</text>')


def arrow(o, x, y1, y2, p):
    o.append(f'<path d="M{x} {y1}V{y2 - 6}" stroke="{p["line"]}"/>')
    o.append(f'<path d="M{x - 4} {y2 - 6}L{x + 4} {y2 - 6}L{x} {y2}Z" fill="{p["line"]}"/>')


def build(p, sg, jb):
    o = []
    a = o.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'role="img" aria-label="Tarkshya Bhardwaj — AI &amp; Security Engineer. LLM engineering, '
      f'agentic AI systems, AI security, and MCP tool boundaries.">')

    a('<defs><style>')
    a(f"@font-face{{font-family:'SG';src:url(data:font/woff2;base64,{sg}) format('woff2');font-weight:100 900}}")
    a(f"@font-face{{font-family:'JB';src:url(data:font/woff2;base64,{jb}) format('woff2');font-weight:400}}")
    a(".m{font-family:'JB',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}")
    a(".d{font-family:'SG',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}")
    for i in range(len(PHRASES)):
        a(f".ph{i}{{animation:vis{i} {CYCLE}s infinite}}")
        a(f".cv{i}{{animation:cur{i} {CYCLE}s infinite}}")
    a("\n".join(type_keyframes()))
    a(f"@keyframes scan{{0%{{transform:translateY(56px)}}100%{{transform:translateY({H-12}px)}}}}")
    a(".scan{animation:scan 7s linear infinite}")
    a("@keyframes blip{0%,100%{opacity:.35}50%{opacity:1}}")
    a(".blip{animation:blip 2.4s ease-in-out infinite}")
    # Reduced motion: freeze on the last phrase, fully typed, and drop the moving parts.
    frozen = round(len(PHRASES[-1]) * CHAR_W, 1)
    a("@media (prefers-reduced-motion:reduce){"
      ".scan,.blip,.pkt,.threat{display:none}"
      ".ph,.cv{animation:none!important}"
      ".ph{opacity:0}"
      f".ph{len(PHRASES)-1}{{opacity:1}}"
      f".cv{len(PHRASES)-1}{{transform:translateX({frozen}px)}}"
      "}")
    a('</style>')

    a(f'<pattern id="g" width="26" height="26" patternUnits="userSpaceOnUse">'
      f'<path d="M26 0H0V26" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>')
    a(f'<linearGradient id="sc"><stop offset="0%" stop-color="{p["accent"]}" stop-opacity="0"/>'
      f'<stop offset="50%" stop-color="{p["accent"]}" stop-opacity="0.45"/>'
      f'<stop offset="100%" stop-color="{p["accent"]}" stop-opacity="0"/></linearGradient>')
    a(f'<clipPath id="card"><rect x="8" y="8" width="{W-16}" height="{H-16}" rx="12"/></clipPath>')

    ty = 240
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>')
    a('<g clip-path="url(#card)">')
    a(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" fill="{p["panel"]}"/>')
    # Grid sits behind the diagram only: the identity panel stays flat so the
    # typing mask can repaint over it without wiping grid lines as it retreats.
    a(f'<rect x="{SPLIT}" y="52" width="{W-8-SPLIT}" height="{H-60}" fill="url(#g)"/>')

    # window chrome
    a(f'<rect x="8" y="8" width="{W-16}" height="44" fill="{p["bar"]}"/>')
    a(f'<path d="M8 52H{W-8}" stroke="{p["line"]}"/>')
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        a(f'<circle cx="{32 + i*20}" cy="30" r="6" fill="{c}"/>')
    a(f'<text x="{W//2}" y="34" class="m" fill="{p["dim"]}" font-size="11.5" '
      f'letter-spacing="0.6" text-anchor="middle">{esc(TITLE)}</text>')
    a(f'<rect class="scan" x="8" y="0" width="{W-16}" height="1.5" fill="url(#sc)"/>')

    # ---- left: identity -----------------------------------------------------
    a(f'<text x="48" y="96" class="m" fill="{p["accent"]}" font-size="10.5" '
      f'letter-spacing="2.4">{esc(EYEBROW)}</text>')
    for i, part in enumerate(NAME):
        a(f'<text x="48" y="{152 + i*44}" class="d" fill="{p["ink"]}" font-size="42" '
          f'font-weight="700" letter-spacing="-0.8">{esc(part)}</text>')

    # typed role line
    a(f'<text x="48" y="{ty}" class="m" fill="{p["accent"]}" font-size="{TYPE_SIZE}">$</text>')
    for i, phrase in enumerate(PHRASES):
        w = round(len(phrase) * CHAR_W, 1)
        a(f'<g class="ph ph{i}">')
        a(f'<text x="76" y="{ty}" class="m" fill="{p["ink"]}" font-size="{TYPE_SIZE}">{esc(phrase)}</text>')
        a(f'<g class="cv cv{i}">'
          f'<rect x="76" y="{ty-13}" width="9" height="17" fill="{p["accent"]}"/>'
          f'<rect x="85" y="{ty-17}" width="{w+24}" height="24" fill="{p["panel"]}"/>'
          f'</g></g>')

    for i, (text, tone) in enumerate(LINES):
        a(f'<text x="48" y="{292 + i*23}" class="d" fill="{p[tone]}" font-size="15">{esc(text)}</text>')

    a(f'<path d="M48 352H500" stroke="{p["line"]}"/>')
    for i, fact in enumerate(FACTS):
        a(f'<text x="48" y="{378 + i*20}" class="m" fill="{p["dim"]}" font-size="10">{esc(fact)}</text>')

    # ---- right: live diagram ------------------------------------------------
    a(f'<path d="M{SPLIT} 72V420" stroke="{p["line"]}"/>')
    a(f'<text x="{SPLIT+40}" y="96" class="m" fill="{p["accent"]}" font-size="10.5" '
      f'letter-spacing="2.4">SYS_ARCH</text>')
    a(f'<circle class="blip" cx="{SPLIT+126}" cy="92" r="3.5" fill="{p["accent"]}"/>')
    a(f'<text x="{SPLIT+138}" y="96" class="m" fill="{p["dim"]}" font-size="10.5" '
      f'letter-spacing="2.4">LIVE</text>')

    bw, bh = 150, 34
    trunk = [("USER", 126), ("AGENT", 196), ("AUTH GATE", 266)]
    for i, (label, y) in enumerate(trunk):
        box(o, CX - bw/2, y, bw, bh, label, p,
            weight="500" if label == "AUTH GATE" else "400",
            stroke=p["accent"] if label == "AUTH GATE" else None)
        if i:
            arrow(o, CX, trunk[i-1][1] + bh, y, p)

    bus_y, leaf_y, lw, gap = 332, 352, 92, 16
    total = len(LEAVES) * lw + (len(LEAVES) - 1) * gap
    x0 = CX - total / 2
    centres = [x0 + i * (lw + gap) + lw / 2 for i in range(len(LEAVES))]
    a(f'<path d="M{CX} {trunk[-1][1] + bh}V{bus_y}" stroke="{p["line"]}"/>')
    a(f'<path d="M{centres[0]} {bus_y}H{centres[-1]}" stroke="{p["line"]}"/>')
    for c, label in zip(centres, LEAVES):
        arrow(o, c, bus_y, leaf_y, p)
        box(o, c - lw/2, leaf_y, lw, 32, label, p, size=10.5)

    # Packets: a steady stream down the trunk, fanning out to a different tool each
    # time. The stagger uses negative begins so every packet is already mid-flight
    # at t=0 — a positive begin parks the circle at the SVG origin until it starts,
    # which shows up as a stray dot in the corner of the card.
    for i, c in enumerate(centres):
        a(f'<circle class="pkt" r="3.5" fill="{p["accent"]}">'
          f'<animateMotion dur="3s" begin="-{i}s" repeatCount="indefinite" '
          f'path="M{CX} {trunk[0][1]+bh} V{bus_y} H{c} V{leaf_y}"/></circle>')

    # and one that gets stopped at the gate
    a(f'<g class="threat"><circle r="3.5" fill="{p["threat"]}">'
      f'<animateMotion dur="9s" repeatCount="indefinite" calcMode="linear" '
      f'keyPoints="0;0;1;1;1" keyTimes="0;0.45;0.62;0.78;1" '
      f'path="M{CX} {trunk[0][1]+bh} V{trunk[2][1]-8}"/>'
      f'<animate attributeName="opacity" dur="9s" repeatCount="indefinite" '
      f'values="0;0;1;1;0;0" keyTimes="0;0.44;0.47;0.74;0.8;1"/></circle>'
      f'<text x="{CX+96}" y="{trunk[2][1]-4}" class="m" fill="{p["threat"]}" font-size="9.5" '
      f'letter-spacing="1.4" text-anchor="middle">REFUSED'
      f'<animate attributeName="opacity" dur="9s" repeatCount="indefinite" '
      f'values="0;0;1;1;0;0" keyTimes="0;0.6;0.64;0.76;0.82;1"/></text></g>')

    a(f'<text x="{SPLIT+40}" y="418" class="m" fill="{p["dim"]}" font-size="10">{esc(CAPTION)}</text>')

    a('</g>')
    a(f'<rect x="8.5" y="8.5" width="{W-17}" height="{H-17}" rx="12" fill="none" stroke="{p["line"]}"/>')
    a('</svg>')
    return "\n".join(o)


def main():
    sg = base64.b64encode((FONTS / "space-grotesk-subset.woff2").read_bytes()).decode()
    jb = base64.b64encode((FONTS / "jetbrains-mono-subset.woff2").read_bytes()).decode()
    for mode, palette in THEME.items():
        path = OUT / f"banner-{mode}.svg"
        path.write_text(build(palette, sg, jb))
        print(f"wrote {path.relative_to(ROOT)}  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
