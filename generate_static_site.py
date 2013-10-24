#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sqlite3
import argparse
import json
from progressbar import ProgressBar
from jinja2 import Environment, PackageLoader

default_out = os.path.join(os.path.dirname(__file__), 'sitio/')
default_db = os.path.join(os.path.dirname(__file__), 'db.db')
DB_JSON = 'db.json'

parser = argparse.ArgumentParser(description='Genera el sitio estático')
parser.add_argument('-f', '--db-file', default = default_db, help = 'Fichero SQLite')
parser.add_argument('-o', '--output', default = default_out, help = 'Directorio de salida del json. Por defecto %s' % default_out)

args = parser.parse_args()

con = sqlite3.connect(args.db_file)
cur = con.cursor()

# Creo el db.json para el buscador client-side

artistas = dict()
q = """ SELECT
            slug, nombre
        FROM artista """
for slug, nombre in cur.execute(q):
    artistas[slug] = nombre

canciones = dict()
total_canciones = cur.execute('SELECT count(*) FROM cancion').fetchone()[0]
q = """ SELECT
            rowid,
            slug_artista,
            slug,
            titulo
        FROM cancion """
pbar = ProgressBar(maxval = total_canciones).start()
pbar.widgets.insert(0, 'Generando db.json... ')
for rowid, slug_artista, slug_cancion, titulo in cur.execute(q):
    anterior = canciones.get(slug_artista, []) # Conservo la lista si existe
    anterior.append(dict(
        s = slug_cancion,
        t = titulo
        ))
    canciones[slug_artista] = anterior
    pbar.update(rowid)
pbar.finish()

f = open(os.path.join(args.output, DB_JSON), 'w')
f.write(json.dumps(dict(
    artistas = artistas,
    canciones = canciones)))
f.close()

env = Environment(loader=PackageLoader('templates','.'))
template_artista = env.get_template('artista.html')
pbar = ProgressBar()
pbar.widgets.insert(0, 'Generando HTMLs para los artistas ... ')
q = """ SELECT slug, nombre FROM artista """
for slug, nombre in pbar(cur.execute(q).fetchall()):
    try:
        os.mkdir(os.path.join(args.output, 'artistas', slug))
    except OSError as e:
        # Ya existe el directorio
        if e.errno == 17:
            pass

    # Busco las canciones del artista
    canciones = []
    q = """ SELECT slug, titulo
            FROM cancion
            WHERE slug_artista=? """
    for slug_c, titulo in cur.execute(q, [slug]):
        canciones.append(dict(titulo=titulo, slug=slug_c))

    render = template_artista.render(nombre = nombre, slug = slug, 
            canciones = canciones)
    f = open(os.path.join(args.output, 'artistas', slug, 'index.html'), 'w')
    f.write(render.encode('utf8'))
    f.close()


