# nini — Portafolio · Constanza Hernández

Portafolio web bilingüe (ES/EN), una sola página con scroll, 8 proyectos con
galería ampliable, hero animado y selector de idioma con persistencia.

## Contenido de la carpeta

```
nini-portafolio/
├── index.html                 ← versión LISTA PARA PUBLICAR (autocontenida, 1 archivo)
├── nini-portafolio.dc.html    ← CÓDIGO FUENTE editable
├── support.js                 ← runtime que necesita el código fuente
├── assets/                    ← todas las imágenes
│   ├── photo-new.jpg          ← foto de "Sobre mí"
│   ├── hd/                     ← imágenes HD de los proyectos (a00–a18)
│   └── sj/                     ← proyecto SmartJob (web01–09, invit1–3, sj_post_latam)
└── README.md
```

## Cómo verlo

- **Rápido / para publicar:** abre `index.html` en el navegador. Funciona solo,
  sin servidor. Este es el archivo que subes a GitHub Pages (junto con `assets/`).
- **Para editar el código:** abre `nini-portafolio.dc.html`. Como carga
  `support.js` y las imágenes por ruta relativa, debes servirlo con un servidor
  local (no funciona con doble clic por las restricciones de `file://`):

  ```bash
  # dentro de la carpeta nini-portafolio/
  python3 -m http.server 8000
  # luego abre http://localhost:8000/nini-portafolio.dc.html
  ```

## Estructura del código (`nini-portafolio.dc.html`)

Es un **Design Component**: un archivo con tres partes.

- **Template (HTML):** todo lo visual, con estilos en línea. Secciones: `nav`,
  `header#top` (hero), marquee, `section#work` (proyectos), `section#about`,
  `section#contact`, footer y el modal de galería.
- **Lógica (`class Component`):** al final, dentro de `<script data-dc-script>`.
  Aquí están:
  - `dict()` → todos los textos en **es** y **en** (edita aquí la copy).
  - `projCopy()` → título, rol, descripción y tags de cada proyecto (es/en).
  - `base()` → color de acento, imagen de portada y año de cada proyecto.
  - `galleries()` → lista de imágenes del modal por proyecto.
  - `toggleLang()`, `openModal()`, `closeModal()` → interacciones.

### Tareas comunes

- **Cambiar un texto:** edítalo en `dict()` (es y en).
- **Agregar/editar un proyecto:** añade una entrada en `base()`, otra en
  `projCopy().es` y `projCopy().en` (mismo índice), y su lista de imágenes en
  `galleries()`. Mantén los tres arreglos alineados por posición.
- **Cambiar el acento de un proyecto:** campo `accent` en `base()`.
- **Color de marca / fondo:** props `accent` (magenta) y `paper`, al final del
  archivo en `data-props`.
- **LinkedIn / CV:** en el template, sección `#contact`, los `<a>`. El de
  LinkedIn ya apunta a tu perfil; el de **CV** tiene `href="#"` — reemplázalo por
  la ruta de tu PDF (ej. `href="cv.pdf" download`) y pon el archivo en la carpeta.

## Publicar en GitHub Pages

1. Sube `index.html` y la carpeta `assets/` a la raíz de un repositorio.
2. Settings → Pages → rama `main`, carpeta `/root`.
3. Tu link queda como `https://tu-usuario.github.io/tu-repo/`.
   (Si el repo se llama `tu-usuario.github.io`, el link va sin la parte final.)

---
Hecho con cariño. © 2025 Constanza Hernández (nini).
