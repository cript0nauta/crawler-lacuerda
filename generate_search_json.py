#-*- coding: utf-8 -*-

import os
import sqlite3
import argparse
import json
from progressbar import ProgressBar

default_out = os.path.join(os.path.dirname(__file__), 'sitio/db.json')
default_db = os.path.join(os.path.dirname(__file__), 'db.db')

parser = argparse.ArgumentParser(description='Genera un fichero JSON para que use el buscador JS')
parser.add_argument('-f', '--db-file', default = default_db, help = 'Fichero SQLite')
parser.add_argument('-o', '--output', default = default_out, help = 'Fichero de salida del json. Por defecto %s' % default_out)

args = parser.parse_args()

con = sqlite3.connect(args.db_file)
cur = con.cursor()

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
for rowid, slug_artista, slug_cancion, titulo in cur.execute(q):
    anterior = canciones.get(slug_artista, []) # Conservo la lista si existe
    anterior.append(dict(
        s = slug_cancion,
        t = titulo
        ))
    canciones[slug_artista] = anterior
    pbar.update(rowid)
pbar.finish()

f = open(args.output, 'w')
f.write(json.dumps(dict(
    artistas = artistas,
    canciones = canciones)))
f.close()

print args.output, 'generado correctamente!'
