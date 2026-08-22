#!/usr/bin/env python3
"""
Generates assets/banner-{dark,light}.svg — the profile hero, in both GitHub themes.

The hero is a terminal window: a system diagram on the left, a SYSTEM:INFO spec
sheet on the right, with a scan line sweeping down the card.

Everything lives here — edit THEME to retheme, SPEC/NODES to change content, then
run `python3 tools/banner.py` from the repo root.

Two things are deliberate:

* The diagram is real SVG geometry, not box-drawing characters. JetBrains Mono
  carries no U+2500 block, so an ASCII diagram would fall back to whatever mono
  font the viewer happens to have and the rules would stop meeting the boxes.
* Fonts are subset to only the glyphs used (~8 KB) and embedded as data URIs.
  GitHub blocks external font loads inside an SVG served as an image, so anything
  not embedded renders in the viewer's system font. Both faces are SIL OFL 1.1.
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets"

W, H = 1200, 460
SPLIT = 508                     # x of the divider between the two panels

THEME = {
    "dark": dict(
        bg="#070a11", panel="#0b0f18", bar="#0e1320", line="#1c2740",
        ink="#e7edf7", muted="#93a1b8", dim="#5a6883", accent="#4d9fff",
        node="#0e1523", grid="rgba(120,150,200,0.05)",
    ),
    "light": dict(
        bg="#f4f6fa", panel="#ffffff", bar="#eef1f7", line="#d8e0ee",
        ink="#0d1520", muted="#48566d", dim="#7b89a0", accent="#1f6feb",
        node="#f7f9fd", grid="rgba(30,50,90,0.05)",
    ),
}

TITLE = "tarkshya@github  —  ~/profile"

# Left panel — the thesis in one picture: nothing reaches real infrastructure
# without clearing an authenticated, scoped gate.
TRUNK = [
    dict(y=122, label="USER",       notes=[]),
    dict(y=196, label="AGENT",      notes=["reasoning · tool choice"]),
    dict(y=270, label="AUTH GATE",  notes=["scoped · least privilege", "audited · refusable"]),
]
LEAVES = ["JIRA", "RISK", "APIs"]
CAPTION = "nothing reaches infrastructure un-scoped"

# Right panel — label / value rows. An empty label opens a new group.
SPEC = [
    ("Subject",   "Tarkshya Bhardwaj"),
    ("Role",      "AI & Security Engineer"),
    ("Origin",    "NIT Srinagar, India"),
    ("Education", "B.Tech Information Technology · 2024—2028"),
    ("Status",    "Building · Learning · Shipping"),
    ("", ""),
    ("Core Lang", "Python · SQL · JavaScript"),
    ("Agents",    "OpenAI Agents SDK · CrewAI · LangGraph · AutoGen"),
    ("Protocol",  "MCP · Tool Calling · Structured Outputs"),
    ("Backend",   "FastAPI · REST · Pydantic"),
    ("Infra",     "AWS EC2 · Amazon Linux · Nginx · Git"),
    ("Security",  "Prompt Injection · Scoped Tools · Risk Workflows"),
    ("", ""),
    ("Currently", "Agentic AI in enterprise security workflows"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def charset():
    """Every glyph the banner draws — feeds the font subsetter."""
    s = TITLE + CAPTION + "SYS_ARCH" + "SYSTEM:INFO" + "".join(LEAVES)
    for n in TRUNK:
        s += n["label"] + "".join(n["notes"])
    for k, v in SPEC:
        s += k + v
    return "".join(sorted(set(s) - {"\n"}))


def box(o, x, y, w, h, label, p, size=11.5, weight="400"):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
             f'fill="{p["node"]}" stroke="{p["line"]}"/>')
    o.append(f'<text x="{x + w/2}" y="{y + h/2 + 4}" class="m" fill="{p["ink"]}" '
             f'font-size="{size}" font-weight="{weight}" letter-spacing="1.1" '
             f'text-anchor="middle">{esc(label)}</text>')


def arrow(o, x, y1, y2, p):
    """Vertical connector from y1 down to y2, with a head at y2."""
    o.append(f'<path d="M{x} {y1}V{y2 - 6}" stroke="{p["line"]}"/>')
    o.append(f'<path d="M{x - 4} {y2 - 6}L{x + 4} {y2 - 6}L{x} {y2}Z" fill="{p["line"]}"/>')


def build(p, sg, jb):
    o = []
    a = o.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'role="img" aria-label="Tarkshya Bhardwaj — AI &amp; Security Engineer. '
      f'Agentic AI, LLM engineering, and AI security.">')

    a('<defs><style>')
    a(f"@font-face{{font-family:'SG';src:url(data:font/woff2;base64,{sg}) format('woff2');font-weight:100 900}}")
    a(f"@font-face{{font-family:'JB';src:url(data:font/woff2;base64,{jb}) format('woff2');font-weight:400}}")
    a(".m{font-family:'JB',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}")
    a(".d{font-family:'SG',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}")
    a(f"@keyframes scan{{0%{{transform:translateY(56px)}}100%{{transform:translateY({H - 12}px)}}}}")
    a(".scan{animation:scan 7s linear infinite}")
    a("@media (prefers-reduced-motion:reduce){.scan{display:none}}")
    a('</style>')
    a(f'<pattern id="g" width="26" height="26" patternUnits="userSpaceOnUse">'
      f'<path d="M26 0H0V26" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>')
    a(f'<linearGradient id="sc"><stop offset="0%" stop-color="{p["accent"]}" stop-opacity="0"/>'
      f'<stop offset="50%" stop-color="{p["accent"]}" stop-opacity="0.45"/>'
      f'<stop offset="100%" stop-color="{p["accent"]}" stop-opacity="0"/></linearGradient>')
    a(f'<clipPath id="card"><rect x="8" y="8" width="{W-16}" height="{H-16}" rx="12"/></clipPath>')
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>')
    a('<g clip-path="url(#card)">')
    a(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" fill="{p["panel"]}"/>')
    a(f'<rect x="8" y="52" width="{W-16}" height="{H-60}" fill="url(#g)"/>')

    # window chrome
    a(f'<rect x="8" y="8" width="{W-16}" height="44" fill="{p["bar"]}"/>')
    a(f'<path d="M8 52H{W-8}" stroke="{p["line"]}"/>')
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        a(f'<circle cx="{32 + i*20}" cy="30" r="6" fill="{c}"/>')
    a(f'<text x="{W//2}" y="34" class="m" fill="{p["dim"]}" font-size="11.5" '
      f'letter-spacing="0.6" text-anchor="middle">{esc(TITLE)}</text>')

    a(f'<rect class="scan" x="8" y="0" width="{W-16}" height="1.5" fill="url(#sc)"/>')

    # ---- left panel ---------------------------------------------------------
    a(f'<text x="44" y="92" class="m" fill="{p["accent"]}" font-size="10.5" '
      f'letter-spacing="2.4">SYS_ARCH</text>')

    cx, bw, bh = 200, 160, 34
    for i, n in enumerate(TRUNK):
        y = n["y"]
        box(a and o, cx - bw/2, y, bw, bh, n["label"], p,
            weight="500" if n["label"] == "AUTH GATE" else "400")
        if i:
            arrow(o, cx, TRUNK[i-1]["y"] + bh, y, p)
        for j, note in enumerate(n["notes"]):
            a(f'<text x="{cx + bw/2 + 24}" y="{y + 16 + j*16}" class="m" fill="{p["dim"]}" '
              f'font-size="10.5">{esc(note)}</text>')

    # fan-out bus
    bus_y, leaf_y, lw, gap = 336, 356, 92, 16
    total = len(LEAVES) * lw + (len(LEAVES) - 1) * gap
    x0 = cx - total / 2
    centres = [x0 + i * (lw + gap) + lw / 2 for i in range(len(LEAVES))]
    a(f'<path d="M{cx} {TRUNK[-1]["y"] + bh}V{bus_y}" stroke="{p["line"]}"/>')
    a(f'<path d="M{centres[0]} {bus_y}H{centres[-1]}" stroke="{p["line"]}"/>')
    for c, label in zip(centres, LEAVES):
        arrow(o, c, bus_y, leaf_y, p)
        box(o, c - lw/2, leaf_y, lw, 32, label, p, size=10.5)

    a(f'<text x="44" y="{leaf_y + 66}" class="m" fill="{p["dim"]}" font-size="10">'
      f'{esc(CAPTION)}</text>')

    # ---- divider + right panel ---------------------------------------------
    a(f'<path d="M{SPLIT} 72V{H - 32}" stroke="{p["line"]}"/>')
    a(f'<text x="{SPLIT + 40}" y="92" class="m" fill="{p["accent"]}" font-size="10.5" '
      f'letter-spacing="2.4">SYSTEM:INFO</text>')

    y = 126
    for label, value in SPEC:
        if not label:
            y += 12
            continue
        a(f'<text x="{SPLIT + 40}" y="{y}" class="m" fill="{p["accent"]}" font-size="12">{esc(label)}</text>')
        a(f'<text x="{SPLIT + 178}" y="{y}" class="m" fill="{p["ink"]}" font-size="12">{esc(value)}</text>')
        y += 23

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
