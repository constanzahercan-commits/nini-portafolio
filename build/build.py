#!/usr/bin/env python3
"""Regenera index.html (la versión publicable) a partir del fuente editable.

Uso, desde la raíz del repo:
    python3 build/build.py

Lee nini-portafolio.dc.html, support.js, assets/foto-flores.jpeg y las
tipografías de build/fonts, y escribe un index.html autocontenido.
Las imágenes de los proyectos NO se incrustan: se cargan desde assets/.
"""
import base64, gzip, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SOURCE = 'nini-portafolio.dc.html'
OUT = 'index.html'

meta = json.load(open('build/embedded.json'))
uuid_of = {v['file']: k for k, v in meta.items() if v['kind'] in ('runtime', 'image')}
RUNTIME_UUID = uuid_of['support.js']
PHOTO_UUID = uuid_of['assets/foto-flores.jpeg']

# 1) fuente -> template que entiende el cargador del bundle
t = open(SOURCE, encoding='utf-8').read()

t = t.replace('./support.js', RUNTIME_UUID)
t = t.replace('assets/foto-flores.jpeg', PHOTO_UUID)

# tipografías: el <link> de Google Fonts se reemplaza por @font-face locales
fonts_css = open('build/fonts.css', encoding='utf-8').read()
t, n = re.subn(r'<link href="https://fonts\.googleapis\.com/css2\?[^>]*>',
               lambda m: '<style>' + fonts_css + '</style>', t)
if n != 1:
    sys.exit('No encontré el <link> de Google Fonts en el fuente (%d)' % n)
t = re.sub(r'<link rel="preconnect"[^>]*>\s*', '', t)

# metadatos que solo usa el empaquetador y el bloque de miniatura
t = re.sub(r'<meta name="ext-resource-dependency"[^>]*>\s*', '', t)
t = re.sub(r'<template id="__bundler_thumbnail">.*?</template>\s*', '', t, flags=re.S)

# 2) manifiesto: runtime, foto y tipografías
manifest = {}
for uuid, m in meta.items():
    raw = open(m['file'], 'rb').read()
    if m.get('compressed'):
        raw = gzip.compress(raw, 9, mtime=0)
    manifest[uuid] = {'mime': m['mime'], 'compressed': bool(m.get('compressed')),
                      'data': base64.b64encode(raw).decode('ascii')}

# 3) ensamblado
def script(kind, payload):
    return '<script type="__bundler/%s">\n%s\n</script>' % (kind, payload)

safe_template = json.dumps(t, ensure_ascii=False).replace('</script', '<\\/script')
out = (open('build/shell_head.html', encoding='utf-8').read()
       + script('manifest', json.dumps(manifest))
       + '\n  '
       + script('ext_resources', '[]')
       + '\n  '
       + script('template', safe_template)
       + open('build/shell_tail.html', encoding='utf-8').read())

open(OUT, 'w', encoding='utf-8').write(out)
print('OK  %s  %.0f KB  (fuente: %s)' % (OUT, len(out) / 1024, SOURCE))
