#!/usr/bin/env python3
"""
Generates assets/stack-{dark,light}.svg — the tech strip, in both GitHub themes.

Logos are Simple Icons paths baked into tools/icons.json, so the strip renders
instantly and identically for everyone instead of depending on a third-party
badge renderer that can rate-limit, restyle, or disappear.

Icons keep their brand colour, except where that colour would vanish into the
background — Ollama and MCP are pure black, which is invisible on a dark card —
so anything past a contrast threshold falls back to the theme's ink.

Simple Icons is CC0-1.0. Run `python3 tools/stack.py` from the repo root.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ICONS = json.loads((ROOT / "tools" / "icons.json").read_text())

W = 1200
PAD = 48
ICON = 30
H = 150

THEME = {
    "dark":  dict(bg="#070a11", panel="#0b0f18", line="#1c2740",
                  accent="#4d9fff", dim="#5a6883", ink="#e7edf7", floor=0.08),
    "light": dict(bg="#f4f6fa", panel="#ffffff", line="#d8e0ee",
                  accent="#1f6feb", dim="#7b89a0", ink="#0d1520", ceil=0.82),
}

# slug -> label shown under the mark
STACK = [
    ("python", "Python"),
    ("fastapi", "FastAPI"),
    ("pydantic", "Pydantic"),
    ("modelcontextprotocol", "MCP"),
    ("langgraph", "LangGraph"),
    ("ollama", "Ollama"),
    ("gradio", "Gradio"),
    ("linux", "Linux"),
    ("nginx", "Nginx"),
    ("git", "Git"),
    ("react", "React"),
    ("tailwindcss", "Tailwind"),
]


def luminance(hex_colour):
    """Relative luminance, WCAG-style, for deciding when a brand colour vanishes."""
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (0, 2, 4))
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def mark_colour(hex_colour, p):
    lum = luminance(hex_colour)
    if "floor" in p and lum < p["floor"]:
        return p["ink"]
    if "ceil" in p and lum > p["ceil"]:
        return p["ink"]
    return "#" + hex_colour


def build(p):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="Stack: {", ".join(l for _, l in STACK)}">']
    o.append(f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>')
    o.append(f'<rect x="8.5" y="8.5" width="{W-17}" height="{H-17}" rx="12" '
             f'fill="{p["panel"]}" stroke="{p["line"]}"/>')
    o.append(f'<text x="{PAD}" y="44" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
             f'fill="{p["accent"]}" font-size="10.5" letter-spacing="2.4">STACK</text>')

    slot = (W - 2 * PAD) / len(STACK)
    scale = ICON / 24
    for i, (slug, label) in enumerate(STACK):
        icon = ICONS[slug]
        cx = PAD + slot * (i + 0.5)
        o.append(f'<g transform="translate({cx - ICON/2:.1f},72) scale({scale})">'
                 f'<path d="{icon["path"]}" fill="{mark_colour(icon["hex"], p)}"/></g>')
        o.append(f'<text x="{cx:.1f}" y="126" text-anchor="middle" '
                 f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
                 f'fill="{p["dim"]}" font-size="9.5" letter-spacing="0.4">{label}</text>')

    o.append('</svg>')
    return "\n".join(o)


def main():
    for mode, palette in THEME.items():
        path = ROOT / "assets" / f"stack-{mode}.svg"
        path.write_text(build(palette))
        print(f"wrote {path.relative_to(ROOT)}  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
