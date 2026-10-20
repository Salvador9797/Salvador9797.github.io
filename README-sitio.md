# Pulso Tech — sitio estático

Blog de noticias de tecnología en español, 100% estático (HTML/CSS/JS sin dependencias), listo para GitHub Pages.

## Flujo de publicación diaria

1. Crear la página del artículo en `articulos/<slug>.html` (copiar una existente y cambiar título, fecha y contenido).
2. Añadir su entrada a `articulos.json` con: slug, titulo, resumen, categoria, fecha (ISO) y url.
3. Ejecutar `python3 generar.py` — regenera el titular destacado, las tarjetas y la cinta de tendencias de `index.html` (el más reciente va primero).
4. Subir todo: `git add . && git commit -m "Artículo del día" && git push`.
5. GitHub Pages publica el sitio automáticamente tras el push.
