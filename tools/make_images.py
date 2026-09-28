"""Generates the site's illustrations as local SVG files (no downloads, no external hosts).
Run:  python3 tools/make_images.py
Names ending in a digit reuse an icon in a shifted colour (tub2 = tub, different hue)."""
import re, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "frontend" / "public" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# icon drawings, centred on 0,0. {F} is the soft fill colour.
ICONS = {
 "barbell": '<path d="M-110 0H110"/><rect x="-84" y="-48" width="14" height="96" rx="3" fill="{F}"/><rect x="-66" y="-34" width="12" height="68" rx="3" fill="{F}"/><rect x="70" y="-48" width="14" height="96" rx="3" fill="{F}"/><rect x="54" y="-34" width="12" height="68" rx="3" fill="{F}"/>',
 "dumbbell": '<path d="M-52 0H52"/><rect x="-92" y="-38" width="40" height="76" rx="9" fill="{F}"/><rect x="52" y="-38" width="40" height="76" rx="9" fill="{F}"/><path d="M-104 -16V16M104 -16V16"/>',
 "kettlebell": '<circle cx="0" cy="22" r="56" fill="{F}"/><path d="M-32 -26C-32 -84 32 -84 32 -26"/><path d="M-24 22H24"/>',
 "glove": '<rect x="-52" y="-64" width="104" height="104" rx="42" fill="{F}"/><ellipse cx="-46" cy="-6" rx="18" ry="26" fill="{F}"/><rect x="-40" y="42" width="80" height="34" rx="6" fill="{F}"/><path d="M-24 -30H26"/>',
 "yoga": '<circle cx="0" cy="-74" r="15" fill="{F}"/><path d="M0 -54V8M0 -40L-32 -86M0 -40L32 -86M0 8L34 58M0 8L-30 30L4 34"/><path d="M-70 68H70"/>',
 "cardio": '<path d="M0 60C-80 0 -70 -70 -30 -70C-10 -70 0 -55 0 -50C0 -55 10 -70 30 -70C70 -70 80 0 0 60Z" fill="{F}"/><path d="M-100 8H-50L-30 -30L-6 40L16 -10L30 8H100"/>',
 "sauna": '<path d="M-50 -20q-16 -22 0 -42q16 -20 0 -40M0 -20q-16 -22 0 -42q16 -20 0 -40M50 -20q-16 -22 0 -42q16 -20 0 -40"/><rect x="-100" y="10" width="200" height="22" rx="4" fill="{F}"/><rect x="-100" y="44" width="200" height="22" rx="4" fill="{F}"/>',
 "studio": '<rect x="-96" y="-76" width="192" height="116" rx="8" fill="{F}"/><path d="M-60 30L-20 -40M20 30L60 -40"/><rect x="-104" y="58" width="208" height="18" rx="9" fill="{F}"/>',
 "rig": '<path d="M-90 74V-70H90V74"/><path d="M-30 -70V30M30 -70V30"/><circle cx="-30" cy="42" r="12" fill="{F}"/><circle cx="30" cy="42" r="12" fill="{F}"/><path d="M-110 74H110"/>',
 "locker": '<rect x="-96" y="-70" width="56" height="140" rx="5" fill="{F}"/><rect x="-28" y="-70" width="56" height="140" rx="5" fill="{F}"/><rect x="40" y="-70" width="56" height="140" rx="5" fill="{F}"/><path d="M-56 -8v16M0 -8v16M68 -8v16"/>',
 "tub": '<rect x="-60" y="-58" width="120" height="28" rx="6" fill="{F}"/><rect x="-54" y="-28" width="108" height="100" rx="10" fill="{F}"/><rect x="-32" y="-6" width="64" height="44" rx="4"/><path d="M-18 10H18M-18 24H8"/>',
 "bottle": '<rect x="-30" y="-78" width="60" height="30" rx="7" fill="{F}"/><rect x="-38" y="-46" width="76" height="120" rx="14" fill="{F}"/><path d="M-38 -6H38M-38 30H38"/>',
 "shirt": '<path d="M-40 -74L-96 -40L-68 0L-46 -18V72H46V-18L68 0L96 -40L40 -74Q0 -46 -40 -74Z" fill="{F}"/>',
 "hoodie": '<path d="M-40 -66L-96 -34L-68 6L-46 -12V72H46V-12L68 6L96 -34L40 -66Q0 -30 -40 -66Z" fill="{F}"/><path d="M-30 -74Q0 -110 30 -74"/><rect x="-32" y="28" width="64" height="30" rx="8"/>',
 "bag": '<rect x="-98" y="-30" width="196" height="96" rx="34" fill="{F}"/><path d="M-42 -30C-42 -86 42 -86 42 -30"/><path d="M-98 18H98"/><circle cx="0" cy="18" r="6" fill="{F}"/>',
 "bands": '<ellipse cx="0" cy="0" rx="96" ry="34" fill="none"/><ellipse cx="0" cy="8" rx="76" ry="52"/><ellipse cx="0" cy="16" rx="56" ry="64" fill="{F}"/>',
 "belt": '<rect x="-104" y="-26" width="208" height="52" rx="12" fill="{F}"/><rect x="-22" y="-40" width="44" height="80" rx="7"/><path d="M-80 0H-40M40 0H80"/>',
 "straps": '<rect x="-104" y="-14" width="208" height="28" rx="8" fill="{F}"/><circle cx="-78" cy="0" r="44"/><circle cx="78" cy="0" r="44"/>',
 "hiit": '<circle cx="0" cy="10" r="64" fill="{F}"/><path d="M-12 -74H12M0 -74V-54"/><path d="M8 -28L-24 18H-2L-10 50L26 0H4Z" fill="{F}"/>',
 "person": '<circle cx="0" cy="-38" r="34" fill="{F}"/><path d="M-76 84Q-76 16 0 16Q76 16 76 84Z" fill="{F}"/>',
}
# base hue per icon
HUE = dict(barbell=215, dumbbell=200, kettlebell=18, glove=352, yoga=165, cardio=340, sauna=28, studio=190,
           rig=42, locker=225, tub=205, bottle=150, shirt=250, hoodie=270, bag=30, bands=310,
           belt=20, straps=55, hiit=8, person=210)

def svg(name):
    m = re.fullmatch(r"([a-z]+?)(\d*)", name)
    icon, n = m.group(1), int(m.group(2) or 0)
    h = (HUE[icon] + 47 * n) % 360
    bg1, bg2 = f"hsl({h} 42% 14%)", f"hsl({(h+25)%360} 48% 26%)"
    acc, fill = f"hsl({h} 92% 72%)", f"hsla({h},90%,72%,.14)"
    shape = ICONS[icon].replace("{F}", fill)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
<radialGradient id="r" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{acc}" stop-opacity=".28"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>
<pattern id="p" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{acc}" stroke-opacity=".07"/></pattern></defs>
<rect width="800" height="600" fill="url(#g)"/><rect width="800" height="600" fill="url(#p)"/><circle cx="400" cy="300" r="300" fill="url(#r)"/>
<g transform="translate(400 300) scale(1.75)" stroke="{acc}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round">{shape}</g></svg>'''

def hero():
    acc = "hsl(215 92% 72%)"
    bars = "".join(f'<path d="M{x} 800L{x+260} 0" stroke="{acc}" stroke-opacity=".05" stroke-width="60"/>' for x in range(-200, 1800, 220))
    bell = ICONS["barbell"].replace("{F}", "hsla(215,90%,72%,.14)")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 800" preserveAspectRatio="xMidYMid slice" role="img">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="hsl(215 45% 12%)"/><stop offset="1" stop-color="hsl(230 50% 24%)"/></linearGradient></defs>
<rect width="1600" height="800" fill="url(#g)"/>{bars}
<g transform="translate(1120 330) scale(4.4)" stroke="{acc}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".9">{bell}</g></svg>'''

names = [f"{i}{n}" if n else i for i in ICONS for n in ("", "2", "3")]
for name in names:
    (OUT / f"{name}.svg").write_text(svg(name))
for i in range(1, 5):
    (OUT / f"person{i}.svg").write_text(svg(f"person{i}"))
for i in range(1, 4):
    (OUT / f"avatar{i}.svg").write_text(svg(f"person{i+4}"))
(OUT / "hero.svg").write_text(hero())
print("wrote", len(list(OUT.glob("*.svg"))), "images to", OUT)
