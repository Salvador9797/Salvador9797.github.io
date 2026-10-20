#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar.py — Regenera las secciones dinámicas de index.html de Pulso Tech
a partir de articulos.json.

Qué regenera (entre marcadores HTML, sin tocar el resto de la página):
  * <!-- INICIO:TICKER -->    ... <!-- FIN:TICKER -->    : titulares de la cinta
  * <!-- INICIO:ARTICULOS --> ... <!-- FIN:ARTICULOS --> : destacado + tarjetas

El artículo más reciente (por fecha ISO) es el destacado (hero) y todas las
entradas aparecen además como tarjetas, de la más nueva a la más vieja.

Uso:
    python3 generar.py

Es idempotente: ejecutarlo varias veces produce el mismo index.html.
"""

import json
import re
import sys
from html import escape
from pathlib import Path

BASE = Path(__file__).resolve().parent
INDEX = BASE / "index.html"
REGISTRO = BASE / "articulos.json"

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

CAMPOS = {"slug", "titulo", "resumen", "categoria", "fecha", "url"}


def fecha_larga(iso: str) -> str:
    """'2026-10-19' -> '19 de octubre de 2026'."""
    anio, mes, dia = iso.split("-")
    return f"{int(dia)} de {MESES[int(mes) - 1]} de {anio}"


def texto_busqueda(a: dict) -> str:
    """Texto en minúsculas para el filtro del buscador (atributo data-buscar)."""
    bruto = f"{a['titulo']} {a['resumen']} {a['categoria']}".lower()
    return escape(bruto, quote=True)


def bloque_ticker(arts: list) -> str:
    piezas = []
    for a in arts:
        piezas.append(
            f'<a href="{escape(a["url"], quote=True)}">{escape(a["titulo"])}</a>'
        )
        piezas.append('<span class="pt-ticker-dot">&#9679;</span>')
    una_vuelta = "\n          ".join(piezas)
    # Dos vueltas idénticas para que la animación de la cinta sea continua.
    return f"{una_vuelta}\n          {una_vuelta}"


def bloque_hero(a: dict) -> str:
    url = escape(a["url"], quote=True)
    return f"""<article class="pt-hero reveal" data-buscar="{texto_busqueda(a)}">
        <p class="pt-kicker">Lo m&#225;s destacado</p>
        <h2><a href="{url}">{escape(a['titulo'])}</a></h2>
        <p class="pt-hero-snippet">{escape(a['resumen'])}</p>
        <div class="pt-meta"><span>{fecha_larga(a['fecha'])}</span><span>&#183; {escape(a['categoria'])}</span></div>
        <a class="pt-cta" href="{url}">Leer art&#237;culo &#8594;</a>
      </article>"""


def bloque_tarjeta(a: dict) -> str:
    url = escape(a["url"], quote=True)
    return f"""<article class="pt-card reveal" data-buscar="{texto_busqueda(a)}">
          <div class="pt-meta"><span>{fecha_larga(a['fecha'])}</span></div>
          <h3><a href="{url}">{escape(a['titulo'])}</a></h3>
          <p class="pt-snippet">{escape(a['resumen'])}</p>
          <div class="pt-labels"><span class="pt-chip">{escape(a['categoria'])}</span></div>
          <a class="pt-more" href="{url}">Leer m&#225;s <span>&#8594;</span></a>
        </article>"""


def bloque_articulos(arts: list) -> str:
    partes = [bloque_hero(arts[0]), '      <div class="pt-grid">']
    partes.extend(bloque_tarjeta(a) for a in arts)
    partes.append("      </div>")
    return "\n".join(partes)


def reemplazar(html: str, inicio: str, fin: str, contenido: str, sangria: str) -> str:
    patron = re.compile(re.escape(inicio) + r".*?" + re.escape(fin), re.DOTALL)
    if not patron.search(html):
        raise SystemExit(
            f"Error: no se encontraron los marcadores {inicio} / {fin} en index.html"
        )
    nuevo = f"{inicio}\n{contenido}\n{sangria}{fin}"
    return patron.sub(lambda _: nuevo, html, count=1)


def main() -> int:
    datos = json.loads(REGISTRO.read_text(encoding="utf-8"))
    arts = datos["articulos"] if isinstance(datos, dict) else datos
    if not arts:
        raise SystemExit("Error: articulos.json no contiene artículos.")
    for a in arts:
        faltan = CAMPOS - a.keys()
        if faltan:
            raise SystemExit(
                f"Error: al artículo '{a.get('slug', '?')}' le faltan campos: "
                f"{sorted(faltan)}"
            )
    # De la más nueva a la más vieja (la fecha ISO ordena bien como texto).
    arts = sorted(arts, key=lambda a: a["fecha"], reverse=True)

    html = INDEX.read_text(encoding="utf-8")
    html = reemplazar(
        html, "<!-- INICIO:TICKER -->", "<!-- FIN:TICKER -->",
        bloque_ticker(arts), "          ",
    )
    html = reemplazar(
        html, "<!-- INICIO:ARTICULOS -->", "<!-- FIN:ARTICULOS -->",
        bloque_articulos(arts), "      ",
    )
    INDEX.write_text(html, encoding="utf-8")
    print(
        f"OK: index.html regenerado con {len(arts)} artículo(s). "
        f"Destacado: {arts[0]['titulo']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
