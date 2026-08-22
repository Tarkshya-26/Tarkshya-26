#!/usr/bin/env python3
"""
Generates assets/banner-{dark,light}.svg — the profile banner, in both GitHub themes.

Everything visual lives here: edit THEME to retheme, edit COPY to change wording,
then run `python3 tools/banner.py` from the repo root.

Space Grotesk and JetBrains Mono are subset to only the glyphs this banner uses
(~7 KB total) and embedded as data URIs, so the type renders identically for every
viewer — GitHub blocks external font loads inside an SVG served as an image.
Both faces are SIL Open Font License 1.1.
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets"

# --- theme -------------------------------------------------------------------
# Drawn from the portfolio's design tokens (src/styles/index.css @theme).
# `accent` is the site's --color-warm; swap in --color-accent #4d9fff for the
# cooler, site-matching variant.
THEME = {
    "dark": dict(
        bg="#08090c", line="#22242b", ink="#f0efec", muted="#9a9992",
        dim="#6a6a66", accent="#f0b35e", grid="rgba(240,235,220,0.045)",
    ),
    "light": dict(
        bg="#faf8f4", line="#e2ddd3", ink="#16171a", muted="#54555a",
        dim="#8a8880", accent="#a06016", grid="rgba(22,23,26,0.05)",
    ),
}

# --- copy --------------------------------------------------------------------
COPY = dict(
    eyebrow="AI &amp; SECURITY ENGINEER",
    place="NIT SRINAGAR &#183; INDIA",
    name="Tarkshya Bhardwaj",
    lead="Building intelligent systems with ",
    lead_hi="security at their core",
    pipeline=["USER", "AGENT", "MCP", "TOOLS", "INFRASTRUCTURE"],
    focus="AGENTIC AI &#183; LLM ENGINEERING &#183; AI SECURITY",
)

TPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360" width="1200" height="360" role="img" aria-label="Tarkshya Bhardwaj — AI &amp; Security Engineer">
  <defs>
    <style>
      @font-face{{font-family:'SG';src:url(data:font/woff2;base64,{sg}) format('woff2');font-weight:100 900;font-style:normal}}
      @font-face{{font-family:'JB';src:url(data:font/woff2;base64,{jb}) format('woff2');font-weight:400;font-style:normal}}
      .d{{font-family:'SG',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}}
      .m{{font-family:'JB',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
    </style>
    <pattern id="g" width="72" height="72" patternUnits="userSpaceOnUse">
      <path d="M72 0H0V72" fill="none" stroke="{grid}" stroke-width="1"/>
    </pattern>
    <radialGradient id="f" cx="46%" cy="42%" r="70%">
      <stop offset="20%" stop-color="#fff" stop-opacity="1"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="mk"><rect width="1200" height="360" fill="url(#f)"/></mask>
  </defs>

  <rect width="1200" height="360" fill="{bg}"/>
  <rect width="1200" height="360" fill="url(#g)" mask="url(#mk)"/>

  <text x="64" y="92" class="m" fill="{accent}" font-size="12" letter-spacing="3.2">{eyebrow}</text>
  <text x="1136" y="92" class="m" fill="{dim}" font-size="12" letter-spacing="3.2" text-anchor="end">{place}</text>

  <text x="64" y="186" class="d" fill="{ink}" font-size="82" font-weight="700" letter-spacing="-1.8">{name}</text>

  <text x="64" y="234" class="d" fill="{muted}" font-size="22" font-weight="400" letter-spacing="-0.3">{lead}<tspan fill="{ink}">{lead_hi}</tspan>.</text>

  <path d="M64 292H1136" stroke="{line}" stroke-width="1"/>

  <text x="64" y="326" class="m" fill="{dim}" font-size="11.5" letter-spacing="2.1">{chain}</text>
  <text x="1136" y="326" class="m" fill="{dim}" font-size="11.5" letter-spacing="2.1" text-anchor="end">{focus}</text>
</svg>
"""


def chain(steps, line):
    """Pipeline steps joined by slashes tinted down to the hairline colour."""
    sep = f'<tspan fill="{line}" dx="9">/</tspan>'
    out = steps[0]
    for step in steps[1:]:
        out += f'{sep}<tspan dx="9">{step}</tspan>'
    return out


def main():
    sg = base64.b64encode((FONTS / "space-grotesk-subset.woff2").read_bytes()).decode()
    jb = base64.b64encode((FONTS / "jetbrains-mono-subset.woff2").read_bytes()).decode()

    for mode, palette in THEME.items():
        svg = TPL.format(sg=sg, jb=jb, **palette, **COPY,
                         chain=chain(COPY["pipeline"], palette["line"]))
        path = OUT / f"banner-{mode}.svg"
        path.write_text(svg)
        print(f"wrote {path.relative_to(ROOT)}  ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
