#!/usr/bin/env python3
"""Genera las 6 imágenes del caso de estudio Neceser (assets/neceser/n01..n06.jpg).
Uso: python3 build/neceser/gen.py   (requiere playwright + chromium)"""
import os, re, io
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'assets', 'neceser')
TMP = os.path.join(os.environ.get('NZ_TMP', '/tmp'), 'neceser_html')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
STK = 'file://' + os.path.join(ROOT, 'assets', 'stickers') + '/'

fonts_css = open(os.path.join(ROOT, 'build', 'fonts.css'), encoding='utf-8').read()
fonts_css = re.sub(r'url\("([0-9a-f\-]{36})"\)', lambda m: 'url("file://%s/build/fonts/%s.woff2")' % (ROOT, m.group(1)), fonts_css)
ds_css = open(os.path.join(ROOT, 'build', 'neceser', 'neceser.css'), encoding='utf-8').read()

# ------------------------------------------------------------------ ilustraciones de producto
def art(kind, c, size=86):
    d = {
      'serum': f'<rect x="38" y="14" width="24" height="16" rx="8" fill="{c}" opacity=".55"/><rect x="42" y="28" width="16" height="12" fill="#2B1633"/><rect x="26" y="38" width="48" height="62" rx="14" fill="{c}"/><rect x="34" y="56" width="32" height="26" rx="6" fill="#fff" opacity=".75"/><rect x="31" y="44" width="6" height="40" rx="3" fill="#fff" opacity=".35"/>',
      'tube': f'<path d="M30 20h40l-4 74H34z" fill="{c}"/><rect x="30" y="10" width="40" height="16" rx="4" fill="#2B1633"/><rect x="38" y="46" width="24" height="22" rx="5" fill="#fff" opacity=".75"/>',
      'lipstick': f'<path d="M36 18l16-8 12 12v22H36z" fill="{c}"/><rect x="32" y="44" width="36" height="14" fill="#2B1633"/><rect x="28" y="58" width="44" height="38" rx="7" fill="#C9A24B"/><rect x="34" y="64" width="6" height="26" rx="3" fill="#fff" opacity=".4"/>',
      'mascara': f'<rect x="44" y="6" width="12" height="38" rx="6" fill="#2B1633"/><rect x="34" y="42" width="32" height="54" rx="9" fill="{c}"/><rect x="40" y="56" width="20" height="22" rx="4" fill="#fff" opacity=".7"/>',
      'jar': f'<rect x="20" y="30" width="60" height="18" rx="7" fill="#2B1633"/><rect x="16" y="46" width="68" height="46" rx="14" fill="{c}"/><rect x="28" y="58" width="44" height="20" rx="6" fill="#fff" opacity=".7"/>',
      'compact': f'<circle cx="50" cy="52" r="38" fill="#2B1633"/><circle cx="50" cy="52" r="29" fill="{c}"/><circle cx="40" cy="44" r="8" fill="#fff" opacity=".35"/>',
    }[kind]
    return f'<svg viewBox="0 0 100 100" width="{size}" height="{size}">{d}</svg>'

PRODUCTS = [
  dict(n='Sérum Vitamina C', b='Lumi Skin', k='serum', c='#FFB347', bg='#FFF0D6', lvl=35, st='soon', tx='21 días'),
  dict(n='Base Velvet 02', b='Aura', k='tube', c='#E8B89A', bg='#FBE9DE', lvl=60, st='fresh', tx='8 meses'),
  dict(n='Labial Rojo Cereza', b='Pétala', k='lipstick', c='#D6254F', bg='#FFE0E6', lvl=80, st='fresh', tx='11 meses'),
  dict(n='Protector SPF50', b='Lumi Skin', k='tube', c='#FFD84D', bg='#FFF6CC', lvl=10, st='soon', tx='9 días'),
  dict(n='Máscara Volumen', b='Aura', k='mascara', c='#7A3CFF', bg='#EFE6FF', lvl=45, st='expired', tx='hace 12 días'),
  dict(n='Crema Hidratante', b='Pétala', k='jar', c='#BFA8FF', bg='#F0EAFF', lvl=70, st='fresh', tx='7 meses'),
  dict(n='Rubor Durazno', b='Aura', k='compact', c='#FF9E8A', bg='#FFE6E0', lvl=90, st='fresh', tx='10 meses'),
  dict(n='Contorno de ojos', b='Lumi Skin', k='tube', c='#7FD8B5', bg='#DDF7EC', lvl=25, st='soon', tx='30 días'),
]
LABEL = {'fresh': 'Fresco', 'soon': 'Vence pronto', 'expired': 'Vencido'}

def pcard(p, w=None, small=False):
    meter = f'<div class="nz-meter {p["st"] if p["st"]!="fresh" else ""}" style="margin-top:8px"><i style="width:{p["lvl"]}%"></i></div>'
    return (f'<div class="nz-card" style="{"width:%dpx;flex:none;" % w if w else ""}">'
            f'<div class="nz-tile" style="background:{p["bg"]};height:{86 if small else 104}px">{art(p["k"], p["c"], 70 if small else 84)}</div>'
            f'<div style="padding:10px 4px 4px"><div style="font-weight:700;font-size:{14.5 if small else 15.5}px;line-height:1.15">{p["n"]}</div>'
            f'<div style="font-size:12.5px;opacity:.6;margin:2px 0 8px">{p["b"]}</div>'
            f'<span class="nz-badge {p["st"]}">{LABEL[p["st"]]}</span>{meter}</div></div>')

# ------------------------------------------------------------------ pantallas (390x844)
def nav(on=0):
    items = [('⌂', 'Inicio'), ('▦', 'Estantes'), None, ('☰', 'Lista'), ('☺', 'Perfil')]
    h = ''
    for i, it in enumerate(items):
        if it is None: h += '<span class="fab">+</span>'
        else: h += f'<span class="{"on" if i == on else ""}"><b>{it[0]}</b>{it[1]}</span>'
    return f'<div class="nav">{h}</div>'

def phone(inner, nv=None, style=''):
    return f'<div class="phone" style="{style}"><div class="notch"></div><div class="scr"><div class="sb"><span>9:41</span><span>●●●</span></div>{inner}</div>{nav(nv) if nv is not None else ""}</div>'

def screen_home():
    stats = ''.join(f'<div style="flex:1;border-radius:18px;padding:12px 12px 10px;background:{bg}"><div class="disp" style="font-weight:800;font-size:28px;line-height:1">{v}</div><div style="font-size:12px;font-weight:600;margin-top:4px;opacity:.75">{t}</div></div>'
                    for v, t, bg in (('86', 'productos', '#fff'), ('7', 'vencen pronto', '#FFE9C2'), ('3', 'vencidos', '#FFD9DE')))
    chips = ''.join(f'<span class="nz-chip {"on" if i == 0 else ""}">{t}</span>' for i, t in enumerate(['Todo', 'Rostro', 'Labios', 'Ojos', 'Piel']))
    soon = ''.join(pcard(PRODUCTS[i], 150, True) for i in (3, 0))
    shelf = ''.join(pcard(PRODUCTS[i], None, True) for i in (2, 6))
    return phone(f'''
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px"><div><div class="mono" style="font-size:12px;opacity:.55">MI NECESER</div><div class="disp" style="font-weight:800;font-size:27px;letter-spacing:-.03em;line-height:1.05">Hola, Vale</div></div>
        <div style="width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#FF2E88,#7A3CFF);border:3px solid #fff"></div></div>
      <div class="nz-input" style="height:46px;font-size:15px">⌕ &nbsp;Buscar producto o marca</div>
      <div style="display:flex;gap:8px">{stats}</div>
      <div style="display:flex;gap:8px;overflow:hidden">{chips}</div>
      <div style="display:flex;justify-content:space-between;align-items:baseline"><b class="disp" style="font-size:19px">Vencen pronto</b><span class="mono" style="font-size:12px;color:var(--nz-rose)">ver todo</span></div>
      <div style="display:flex;gap:12px;overflow:hidden">{soon}</div>
      <div><b class="disp" style="font-size:19px">Mis estantes</b></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">{shelf}</div>''', nv=0)

def screen_detail():
    p = PRODUCTS[0]
    return phone(f'''
      <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:24px">‹</span><span class="mono" style="font-size:12px;opacity:.55">DETALLE</span><span style="font-size:22px">⋯</span></div>
      <div class="nz-tile" style="background:{p['bg']};height:230px;border-radius:30px;position:relative">{art(p['k'], p['c'], 170)}<span class="nz-badge soon" style="position:absolute;left:14px;top:14px;background:#fff">Vence en 21 días</span></div>
      <div><div class="disp" style="font-weight:800;font-size:29px;letter-spacing:-.03em;line-height:1.05">{p['n']}</div><div style="opacity:.6;font-size:15px;margin-top:3px">{p['b']} · Rostro · Sérum</div></div>
      <div style="display:flex;gap:10px">
        <div class="nz-card" style="flex:1;padding:12px"><div class="mono" style="font-size:11px;opacity:.55">ABIERTO</div><b class="disp" style="font-size:19px">12 mar</b></div>
        <div class="nz-card" style="flex:1;padding:12px"><div class="mono" style="font-size:11px;opacity:.55">PAO</div><b class="disp" style="font-size:19px">12 meses</b></div>
        <div class="nz-card" style="flex:1;padding:12px"><div class="mono" style="font-size:11px;opacity:.55">USADO EN</div><b class="disp" style="font-size:19px">3 videos</b></div></div>
      <div><div style="display:flex;justify-content:space-between;font-weight:600;font-size:15px;margin-bottom:8px"><span>Queda</span><span>35%</span></div><div class="nz-meter soon" style="height:12px"><i style="width:35%"></i></div></div>
      <div class="nz-card" style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px"><span style="font-weight:600">Avisarme 30 días antes</span><span class="nz-toggle"></span></div>
      <div style="display:flex;gap:10px"><span class="nz-btn pri" style="flex:1.3">Lo terminé</span><span class="nz-btn" style="flex:1">A la lista</span></div>''')

def screen_scan():
    corners = ''.join(f'<i style="position:absolute;{pos};width:44px;height:44px;border:5px solid var(--nz-lime);{bd};border-radius:{rd}"></i>' for pos, bd, rd in (
        ('left:0;top:0', 'border-right:0;border-bottom:0', '18px 0 0 0'), ('right:0;top:0', 'border-left:0;border-bottom:0', '0 18px 0 0'),
        ('left:0;bottom:0', 'border-right:0;border-top:0', '0 0 0 18px'), ('right:0;bottom:0', 'border-left:0;border-top:0', '0 0 18px 0')))
    bars = ''.join(f'<i style="display:block;width:{w}px;height:78px;background:#fff;margin-right:{g}px"></i>' for w, g in ((3, 4), (6, 3), (2, 5), (5, 3), (3, 6), (7, 3), (2, 4), (5, 5), (3, 3), (6, 4), (2, 3)))
    return phone(f'''
      <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:24px">✕</span><span class="mono" style="font-size:12px;opacity:.55">AGREGAR</span><span></span></div>
      <div style="border-radius:30px;background:#2B1633;height:300px;position:relative;display:flex;align-items:center;justify-content:center;padding:30px"><div style="position:absolute;inset:34px">{corners}</div><div style="display:flex;align-items:center">{bars}</div><div style="position:absolute;left:50px;right:50px;top:50%;height:3px;background:var(--nz-rose);box-shadow:0 0 18px var(--nz-rose)"></div></div>
      <div class="disp" style="font-weight:800;font-size:25px;letter-spacing:-.02em;line-height:1.1">Escanea el código de barras</div>
      <div style="font-size:15px;opacity:.65;margin-top:-6px">Llenamos nombre, marca y PAO por ti. Puedes editarlo después.</div>
      <div class="mono" style="font-size:12px;opacity:.55;margin-top:4px">¿CÓMO LLEGÓ A TU NECESER?</div>
      <div style="display:flex;gap:8px"><span class="nz-chip">Compra</span><span class="nz-chip on" style="background:#5B2BD6;border-color:#5B2BD6">PR / regalo</span><span class="nz-chip">Colab</span></div>
      <div class="nz-input">☰ &nbsp;Agregar manualmente</div>
      <span class="nz-btn pri" style="width:100%;margin-top:4px">Guardar en mi neceser</span>''')

def screen_buy():
    a, b = PRODUCTS[2], dict(PRODUCTS[2], n='Rojo Cereza Mate', b='Pétala')
    items = [('Protector SPF50', 'queda 10%', '$14.990', True), ('Contorno de ojos', 'queda 25%', '$21.990', False), ('Pestañina waterproof', 'nuevo', '$11.990', False)]
    rows = ''.join(f'<div style="display:flex;align-items:center;gap:12px;padding:11px 0;border-top:1px solid var(--nz-line)"><span class="nz-check {"on" if on else ""}">{"✓" if on else ""}</span><div style="flex:1"><div style="font-weight:600;font-size:15px">{n}</div><div style="font-size:12.5px;opacity:.55">{s}</div></div><b style="font-size:14.5px">{pr}</b></div>' for n, s, pr, on in items)
    return phone(f'''
      <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:24px">‹</span><span class="mono" style="font-size:12px;opacity:.55">ANTES DE COMPRAR</span><span></span></div>
      <div style="border-radius:28px;background:linear-gradient(160deg,#FFE0EE,#EADFFF);padding:18px;border:1.5px solid rgba(255,46,136,.35)">
        <span class="nz-badge" style="background:var(--nz-rose);color:#fff">Ojo</span>
        <div class="disp" style="font-weight:800;font-size:25px;letter-spacing:-.025em;line-height:1.1;margin:10px 0 6px">Ya tienes 2 rojos parecidos</div>
        <div style="font-size:14.5px;opacity:.7;margin-bottom:14px">Labial Rojo Cereza (Pétala) y Rojo Amor (Aura) tienen un tono muy cercano.</div>
        <div style="display:flex;gap:10px"><div class="nz-tile" style="flex:1;background:#fff;height:92px">{art('lipstick', '#D6254F', 64)}</div><div class="nz-tile" style="flex:1;background:#fff;height:92px">{art('lipstick', '#C41E3A', 64)}</div><div class="nz-tile" style="flex:1;background:#FFD9E5;height:92px;border:2px dashed var(--nz-rose)">{art('lipstick', '#DC143C', 64)}</div></div>
      </div>
      <div style="display:flex;gap:10px"><span class="nz-btn dark" style="flex:1.2">Mejor no</span><span class="nz-btn ghost" style="flex:1">Agregar igual</span></div>
      <div><div style="display:flex;justify-content:space-between;align-items:baseline"><b class="disp" style="font-size:19px">Lista de compras</b><span class="mono" style="font-size:12px;opacity:.55">$48.970</span></div>{rows}</div>''', nv=3)

def screen_creator():
    ids = [2, 6, 0, 5, 1, 3]
    CK='<span style="position:absolute;right:6px;top:6px;width:24px;height:24px;border-radius:50%;background:var(--nz-rose);color:#fff;font-size:14px;font-weight:700;display:flex;align-items:center;justify-content:center">✓</span>'
    def tile(i):
        on = i in (2, 0, 1)
        bd = 'var(--nz-rose)' if on else 'transparent'
        return f'<div style="position:relative;border-radius:18px;background:{PRODUCTS[i]["bg"]};height:116px;display:flex;align-items:center;justify-content:center;border:3px solid {bd}">{art(PRODUCTS[i]["k"], PRODUCTS[i]["c"], 78)}{CK if on else ""}</div>'
    tiles = ''.join(tile(i) for i in ids)
    return phone(f'''
      <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:24px">‹</span><span class="mono" style="font-size:12px;opacity:.55">MODO CREADORA</span><span></span></div>
      <div class="disp" style="font-weight:800;font-size:27px;letter-spacing:-.03em;line-height:1.05">Estante para contenido</div>
      <div style="display:flex;gap:8px;overflow:hidden"><span class="nz-chip on">Todo</span><span class="nz-chip">PR · 6</span><span class="nz-chip">Colab · 2</span><span class="nz-chip">Terminados</span></div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">{tiles}</div>
      <div class="nz-card" style="display:flex;align-items:center;gap:12px;padding:12px 14px"><span class="nz-badge pr">Colaboración</span><span style="font-size:13.5px;line-height:1.25">Se agrega la etiqueta de publicidad al exportar</span></div>
      <span class="nz-btn pri" style="width:100%">Exportar para stories ↗</span>''', nv=1)

# ------------------------------------------------------------------ marco de cada lámina
def slide(body, bg='var(--nz-blush)', idx=1, dark=False, label='NECESER · CASO DE ESTUDIO'):
    col = '#fff' if dark else 'var(--nz-plum)'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{fonts_css}{ds_css}
      html,body{{width:1920px;height:1080px;overflow:hidden}}
      .sl{{position:relative;width:1920px;height:1080px;background:{bg};color:{col};overflow:hidden}}
      .dots{{position:absolute;inset:0;background-image:radial-gradient({'rgba(255,255,255,.12)' if dark else 'rgba(43,22,51,.13)'} 1.5px,transparent 1.7px);background-size:34px 34px}}
      .top{{position:absolute;left:96px;right:96px;top:56px;display:flex;justify-content:space-between;font-family:'Space Mono',monospace;font-size:20px;letter-spacing:.14em;opacity:.65;z-index:5}}
      .stk{{position:absolute;z-index:8}} .stk img{{display:block;width:100%}}
    </style></head><body><div class="sl"><div class="dots"></div>
      <div class="top"><span>{label}</span><span>0{idx} / 06</span></div>{body}</div></body></html>'''

def stk(name, style):
    return f'<div class="stk" style="{style}"><img src="{STK}{name}.svg"></div>'

SLIDES = {}

# n01 · portada
SLIDES['n01'] = slide(f'''
  <div style="position:absolute;inset:0;background:radial-gradient(900px circle at 82% 38%,rgba(255,46,136,.28),transparent 60%),radial-gradient(700px circle at 8% 100%,rgba(217,255,63,.45),transparent 60%),radial-gradient(800px circle at 95% 95%,rgba(122,60,255,.22),transparent 60%)"></div>
  <div style="position:absolute;left:96px;top:236px;width:900px;z-index:4">
    <div class="mono" style="font-size:24px;letter-spacing:.16em;opacity:.7">APP · CONCEPTO · 2026</div>
    <div class="disp" style="font-weight:800;font-size:250px;line-height:.86;letter-spacing:-.055em;margin-top:22px">Neceser<span style="color:var(--nz-rose)">.</span></div>
    <div class="disp" style="font-weight:700;font-size:58px;letter-spacing:-.03em;margin-top:30px;line-height:1.05">Tu neceser, bajo control.</div>
    <div style="font-size:32px;line-height:1.45;margin-top:22px;max-width:760px;opacity:.85">Inventario de cosmética para beauty vloggers e influencers: qué tienes, cuánto te queda y qué vence antes de grabar.</div>
    <div style="display:flex;gap:14px;margin-top:38px"><span class="nz-chip on" style="height:52px;font-size:21px;padding:0 24px">UX/UI</span><span class="nz-chip" style="height:52px;font-size:21px;padding:0 24px">Design system</span><span class="nz-chip" style="height:52px;font-size:21px;padding:0 24px">App móvil</span></div>
  </div>
  <div style="position:absolute;left:1040px;top:150px;width:900px;height:900px;z-index:3">
    <div style="position:absolute;left:0;top:130px;transform:scale(.78) rotate(-7deg);transform-origin:top left">{screen_detail()}</div>
    <div style="position:absolute;left:560px;top:150px;transform:scale(.78) rotate(7deg);transform-origin:top left">{screen_buy()}</div>
    <div style="position:absolute;left:276px;top:56px;transform:scale(.92);transform-origin:top left;z-index:4">{screen_home()}</div>
  </div>
  {stk('sticker-burst-mag', 'left:770px;top:150px;width:220px;transform:rotate(-10deg)')}
  <div class="hand" style="position:absolute;left:808px;top:226px;width:150px;text-align:center;font-size:36px;color:#fff;transform:rotate(-10deg);z-index:9">concepto</div>
  {stk('sticker-smile', 'left:1790px;top:150px;width:120px;transform:rotate(12deg)')}
  {stk('sticker-heart', 'left:70px;top:900px;width:120px;transform:rotate(-8deg)')}
''', idx=1)

# n02 · problema y propuesta
pain = [('Compro de más', 'Productos repetidos que se acumulan porque no sé qué tengo.'), ('Se me vencen', 'Abro algo y pierdo la cuenta de cuándo, hasta que ya no sirve.'), ('Se me pierde lo del contenido', 'Entre PR, colaboraciones y compras, no sé qué puedo mostrar ni cuándo.')]
sol = [('Todo en un lugar', 'Escaneas el código y queda con marca, PAO y fecha de apertura.'), ('Avisa a tiempo', 'Alertas antes de que venza y nivel de producto para saber cuándo reponer.'), ('Pensada para crear', 'Etiquetas de PR y colaboración, estante para contenido y terminados.')]
def col(items, ok):
    h = ''
    for t, d in items:
        h += (f'<div style="display:flex;gap:26px;align-items:flex-start;background:#fff;border-radius:30px;padding:22px 30px;border:2px solid {"rgba(47,191,122,.5)" if ok else "var(--nz-line)"};box-shadow:0 22px 40px -30px rgba(43,22,51,.5)">'
              f'<div style="flex:none;width:56px;height:56px;border-radius:50%;background:{"var(--nz-fresh)" if ok else "var(--nz-expired)"};color:#fff;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700">{"✓" if ok else "✕"}</div>'
              f'<div><div class="disp" style="font-weight:700;font-size:38px;letter-spacing:-.02em;line-height:1.05">{t}</div><div style="font-size:24px;line-height:1.35;margin-top:6px;opacity:.75">{d}</div></div></div>')
    return h
SLIDES['n02'] = slide(f'''
  <div style="position:absolute;left:96px;top:110px;right:96px;z-index:4">
    <div class="disp" style="font-weight:800;font-size:92px;letter-spacing:-.045em;line-height:.95">De acumular a<br>tener el control<span style="color:var(--nz-rose)">.</span></div>
  </div>
  <div style="position:absolute;left:96px;top:360px;width:790px;display:flex;flex-direction:column;gap:22px;z-index:4">
    <div class="mono" style="font-size:22px;letter-spacing:.14em;opacity:.6;margin-bottom:2px">EL PROBLEMA</div>{col(pain, False)}</div>
  <div style="position:absolute;left:1034px;top:360px;width:790px;display:flex;flex-direction:column;gap:22px;z-index:4">
    <div class="mono" style="font-size:22px;letter-spacing:.14em;color:var(--nz-rose);margin-bottom:2px">LA PROPUESTA</div>{col(sol, True)}</div>
  <img src="{STK}arrow.svg" style="position:absolute;left:880px;top:520px;width:150px;transform:rotate(80deg);z-index:6">
  
  {stk('sparkle-lime', 'right:120px;top:130px;width:110px')}
''', idx=2)

# n03 · fundamentos del design system
def sw(name, hexv, fg='#fff', w=300, h=170, note=''):
    nt = f'<div style="font-size:19px;opacity:.65;margin-top:10px">{note}</div>' if note else ''
    return f'<div style="width:{w}px"><div style="height:{h}px;border-radius:26px;background:{hexv};color:{fg};padding:18px 20px;display:flex;flex-direction:column;justify-content:flex-end;box-shadow:0 18px 30px -22px rgba(43,22,51,.6)"><div class="disp" style="font-weight:700;font-size:27px;line-height:1">{name}</div><div class="mono" style="font-size:18px;opacity:.8;margin-top:5px">{hexv}</div></div>{nt}</div>'
SLIDES['n03'] = slide(f'''
  <div style="position:absolute;left:96px;top:130px;z-index:4"><div class="disp" style="font-weight:800;font-size:92px;letter-spacing:-.045em;line-height:.95">Fundamentos<span style="color:var(--nz-rose)">.</span></div>
    <div style="font-size:30px;opacity:.7;margin-top:14px">Color, tipografía y forma para una app cálida, clara y fácil de escanear.</div></div>
  <div style="position:absolute;left:96px;top:370px;z-index:4">
    <div class="mono" style="font-size:20px;letter-spacing:.14em;opacity:.6;margin-bottom:16px">MARCA</div>
    <div style="display:flex;gap:22px">{sw('Rose','#FF2E88',note='Acción principal')}{sw('Plum','#2B1633',note='Texto y navegación')}{sw('Lime','#D9FF3F','#2B1633',note='Foco y acentos')}{sw('Lavender','#E9DDFF','#2B1633',note='PR y colaboración')}</div>
    <div class="mono" style="font-size:20px;letter-spacing:.14em;opacity:.6;margin:34px 0 16px">ESTADO DEL PRODUCTO</div>
    <div style="display:flex;gap:22px">{sw('Fresco','#2FBF7A',w=300,h=120,note='Dentro del PAO')}{sw('Vence pronto','#FFA826','#2B1633',w=300,h=120,note='30 días o menos')}{sw('Vencido','#F2475A',w=300,h=120,note='Pasó su fecha')}<div style="width:300px"><div style="height:120px;border-radius:26px;background:#fff;border:2px solid var(--nz-line);padding:18px 20px;display:flex;flex-direction:column;justify-content:flex-end"><div class="disp" style="font-weight:700;font-size:27px;line-height:1">Neutros</div><div class="mono" style="font-size:18px;opacity:.7;margin-top:5px">#FBF6F1 · #FFF1F6</div></div><div style="font-size:19px;opacity:.65;margin-top:10px">Fondos de la app</div></div></div>
  </div>
  <div style="position:absolute;left:1480px;top:370px;width:360px;z-index:4">
    <div class="mono" style="font-size:20px;letter-spacing:.14em;opacity:.6;margin-bottom:16px">TIPOGRAFÍA</div>
    <div style="background:#fff;border-radius:30px;padding:26px 28px;border:2px solid var(--nz-line);box-shadow:0 22px 40px -30px rgba(43,22,51,.5)">
      <div class="disp" style="font-weight:800;font-size:96px;letter-spacing:-.05em;line-height:.9">Aa</div>
      <div class="disp" style="font-weight:700;font-size:26px;margin-top:10px">Bricolage Grotesque</div><div style="font-size:19px;opacity:.6">Títulos y números</div>
      <div style="height:1px;background:var(--nz-line);margin:16px 0"></div>
      <div style="font-weight:600;font-size:26px">Instrument Sans</div><div style="font-size:19px;opacity:.6">Interfaz y lectura</div>
      <div style="height:1px;background:var(--nz-line);margin:16px 0"></div>
      <div class="mono" style="font-weight:700;font-size:23px">Space Mono</div><div style="font-size:19px;opacity:.6">Fechas, PAO y datos</div></div>
    <div style="display:flex;gap:12px;margin-top:22px"><div style="flex:1;background:var(--nz-plum);color:#fff;border-radius:16px;height:84px;display:flex;align-items:center;justify-content:center;font-size:20px" class="mono">radio 16</div><div style="flex:1;background:var(--nz-plum);color:#fff;border-radius:100px;height:84px;display:flex;align-items:center;justify-content:center;font-size:20px" class="mono">pill</div></div>
  </div>
  {stk('asterisk', 'right:260px;top:150px;width:90px')}
''', idx=3)

# n04 · componentes
def box(title, inner, w, h=None):
    return f'<div style="width:100%;box-sizing:border-box;{f"height:{h}px;" if h else ""}background:#fff;border-radius:30px;padding:24px 28px 28px;border:2px solid var(--nz-line);box-shadow:0 22px 40px -32px rgba(43,22,51,.55)"><div class="mono" style="font-size:18px;letter-spacing:.14em;opacity:.55;margin-bottom:18px">{title}</div>{inner}</div>'
SLIDES['n04'] = slide(f'''
  <div style="position:absolute;left:96px;top:130px;z-index:4"><div class="disp" style="font-weight:800;font-size:92px;letter-spacing:-.045em;line-height:.95">Componentes<span style="color:var(--nz-rose)">.</span></div></div>
  <div style="position:absolute;left:96px;top:290px;width:1730px;display:grid;grid-template-columns:repeat(12,1fr);gap:26px;z-index:4">
    <div style="grid-column:span 5">{box('BOTONES', '<div style="display:flex;flex-wrap:wrap;gap:14px"><span class="nz-btn pri">Guardar</span><span class="nz-btn dark">Mejor no</span><span class="nz-btn">Secundario</span><span class="nz-btn ghost">Terciario</span><span class="nz-btn pri dis">Deshabilitado</span></div>', 0)}</div>
    <div style="grid-column:span 4">{box('CHIPS Y ESTADOS', '<div style="display:flex;flex-wrap:wrap;gap:10px"><span class="nz-chip on">Todo</span><span class="nz-chip">Rostro</span><span class="nz-chip">Labios</span></div><div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:16px"><span class="nz-badge fresh">Fresco</span><span class="nz-badge soon">Vence pronto</span><span class="nz-badge expired">Vencido</span><span class="nz-badge pr">PR</span></div>', 0)}</div>
    <div style="grid-column:span 3">{box('NIVEL DE PRODUCTO', '<div style="display:flex;flex-direction:column;gap:20px"><div><div style="display:flex;justify-content:space-between;font-size:20px;font-weight:600;margin-bottom:8px"><span>Base</span><span>80%</span></div><div class="nz-meter" style="height:12px"><i style="width:80%"></i></div></div><div><div style="display:flex;justify-content:space-between;font-size:20px;font-weight:600;margin-bottom:8px"><span>Sérum</span><span>35%</span></div><div class="nz-meter soon" style="height:12px"><i style="width:35%"></i></div></div><div><div style="display:flex;justify-content:space-between;font-size:20px;font-weight:600;margin-bottom:8px"><span>SPF</span><span>10%</span></div><div class="nz-meter expired" style="height:12px"><i style="width:10%"></i></div></div></div>', 0)}</div>
    <div style="grid-column:span 5">{box('TARJETA DE PRODUCTO', f'<div style="display:flex;gap:18px">{pcard(PRODUCTS[0], 250)}{pcard(PRODUCTS[4], 250)}</div>', 0)}</div>
    <div style="grid-column:span 4">{box('CAMPOS Y CONTROLES', '<div class="nz-input" style="margin-bottom:14px">⌕ &nbsp;Buscar producto o marca</div><div class="nz-card" style="display:flex;justify-content:space-between;align-items:center;padding:14px 18px;margin-bottom:14px"><span style="font-weight:600;font-size:18px">Avisarme 30 días antes</span><span class="nz-toggle"></span></div><div style="display:flex;gap:30px;align-items:center"><span class="nz-check on">✓</span><span class="nz-check"></span><span class="nz-toggle off"></span></div>', 0)}</div>
    <div style="grid-column:span 3">{box('NAVEGACIÓN', '<div style="position:relative;height:84px;border-radius:30px;background:var(--nz-plum);display:flex;align-items:center;justify-content:space-around;color:#fff;font-size:22px"><span style="color:var(--nz-lime)">⌂</span><span style="opacity:.6">▦</span><span style="width:60px;height:60px;border-radius:50%;background:var(--nz-rose);display:flex;align-items:center;justify-content:center;font-size:34px;margin-top:-34px;border:5px solid #fff">+</span><span style="opacity:.6">☰</span><span style="opacity:.6">☺</span></div><div style="font-size:19px;opacity:.65;margin-top:18px;line-height:1.35">Botón central siempre visible para agregar o escanear.</div>', 0)}</div>
  </div>
  {stk('sticker-bolt', 'right:130px;top:90px;width:110px;transform:rotate(10deg)')}
''', idx=4)

# n05 · pantallas clave
cap = lambda n, t, d: f'<div style="width:390px;margin-top:26px"><div class="mono" style="font-size:20px;color:var(--nz-rose);letter-spacing:.1em">{n}</div><div class="disp" style="font-weight:700;font-size:31px;letter-spacing:-.02em;line-height:1.1;margin-top:4px">{t}</div><div style="font-size:21px;opacity:.65;margin-top:4px;line-height:1.35">{d}</div></div>'
SLIDES['n05'] = slide(f'''
  <div style="position:absolute;left:96px;top:128px;z-index:4"><div class="disp" style="font-weight:800;font-size:80px;letter-spacing:-.045em;line-height:.95">Cuatro pantallas clave<span style="color:var(--nz-rose)">.</span></div></div>
  <div style="position:absolute;left:96px;top:250px;display:flex;gap:56px;z-index:4;transform-origin:top left">
    <div style="width:390px">{'<div style="transform:scale(.78);transform-origin:top left;height:658px;width:304px">' + screen_home() + '</div>'}{cap('01', 'Ver todo', 'Vencimientos primero, estantes después.')}</div>
    <div style="width:390px">{'<div style="transform:scale(.78);transform-origin:top left;height:658px;width:304px">' + screen_detail() + '</div>'}{cap('02', 'Detalle', 'Apertura, PAO, nivel y uso en videos.')}</div>
    <div style="width:390px">{'<div style="transform:scale(.78);transform-origin:top left;height:658px;width:304px">' + screen_scan() + '</div>'}{cap('03', 'Agregar', 'Escanea y marca si fue compra, PR o colab.')}</div>
    <div style="width:390px">{'<div style="transform:scale(.78);transform-origin:top left;height:658px;width:304px">' + screen_buy() + '</div>'}{cap('04', 'Antes de comprar', 'Avisa si ya tienes algo parecido.')}</div>
  </div>
  <img src="{STK}arrow.svg" style="position:absolute;left:560px;top:270px;width:110px;transform:rotate(-8deg);z-index:6;opacity:0">
''', idx=5)

# n06 · modo creadora
feat = [('Etiquetas de PR y colaboración', 'Cada producto recuerda cómo llegó y avisa cuándo corresponde declarar la publicidad.'), ('Estante para contenido', 'Selecciona productos y exporta un collage listo para stories o miniaturas.'), ('Antes de grabar', 'Revisa qué vence pronto para usarlo en cámara y no perderlo.'), ('Terminados', 'Un registro de lo que ya acabaste, con costo por uso.')]
fh = ''.join(f'<div style="display:flex;gap:24px;align-items:flex-start;background:#fff;border-radius:28px;padding:26px 30px;border:2px solid var(--nz-line);box-shadow:0 22px 40px -32px rgba(43,22,51,.55)"><div class="mono" style="flex:none;font-size:22px;color:var(--nz-rose);font-weight:700;margin-top:4px">0{i + 1}</div><div><div class="disp" style="font-weight:700;font-size:35px;letter-spacing:-.02em;line-height:1.05">{t}</div><div style="font-size:24px;line-height:1.4;opacity:.7;margin-top:6px">{d}</div></div></div>' for i, (t, d) in enumerate(feat))
SLIDES['n06'] = slide(f'''
  <div style="position:absolute;inset:0;background:radial-gradient(700px circle at 20% 55%,rgba(122,60,255,.22),transparent 60%),radial-gradient(600px circle at 95% 10%,rgba(255,46,136,.2),transparent 60%)"></div>
  <div style="position:absolute;left:96px;top:128px;z-index:4"><div class="disp" style="font-weight:800;font-size:80px;letter-spacing:-.045em;line-height:.95">Modo creadora<span style="color:var(--nz-rose)">.</span></div></div>
  <div style="position:absolute;left:150px;top:230px;transform:scale(.97);transform-origin:top left;z-index:4">{screen_creator()}</div>
  <div style="position:absolute;left:660px;top:262px;width:1160px;display:flex;flex-direction:column;gap:22px;z-index:4">{fh}</div>
  {stk('sticker-burst', 'left:400px;top:190px;width:200px;transform:rotate(10deg)')}
  <div class="hand" style="position:absolute;left:420px;top:262px;width:160px;text-align:center;line-height:1;font-size:32px;color:#fff;transform:rotate(10deg);z-index:9">para<br>creadoras</div>
  {stk('sticker-heart', 'left:70px;top:900px;width:110px;transform:rotate(-8deg)')}
''', idx=6)

if __name__ == '__main__':
    only = os.environ.get('ONLY')
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1920, 'height': 1080})
        for name, html in SLIDES.items():
            if only and name != only: continue
            f = os.path.join(TMP, name + '.html'); open(f, 'w', encoding='utf-8').write(html)
            pg.goto('file://' + f); pg.wait_for_timeout(500)
            png = pg.screenshot(type='png')
            Image.open(io.BytesIO(png)).convert('RGB').save(os.path.join(OUT, name + '.jpg'), quality=86, optimize=True, progressive=True)
            print('ok', name, os.path.getsize(os.path.join(OUT, name + '.jpg')) // 1024, 'KB')
        b.close()
