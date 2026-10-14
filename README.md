# Portafolio de Constanza (nini)

Sitio en GitHub Pages, dominio ninidesign.cl (ver CNAME).

## Cómo editar

1. Edita `nini-portafolio.dc.html` (es la única fuente: estilos, textos, proyectos).
2. Corre `python3 build/build.py`. Eso regenera `index.html`, que es lo que se publica.
3. Abre `index.html` con doble clic para revisar. Sube los cambios a GitHub.

No edites `index.html` a mano, se sobrescribe en cada build.

## Carpetas

- `assets/` imágenes de proyectos (JPG optimizados).
- `build/` build.py, fuentes embebidas, shell del bundle.

## Agregar un proyecto

Agrega sus textos en `projCopy()`, una entrada en `base()` (color, imagen, tamaño en el grid) y su galería en `galleries()`.
