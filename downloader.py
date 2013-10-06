#-*- coding: utf-8 -*-

import os
import sys
import argparse
import sqlite3
import crawler

default_db = os.path.join(os.path.dirname(__file__), 'db.db')
tables_file = os.path.join(os.path.dirname(__file__), 'db.sql')

parser = argparse.ArgumentParser(description = 'Descarga todas las versiones de las canciones y las almacena en una base de datos SQLite')
parser.add_argument('-f', '--file', default = default_db, help = 'Fichero SQLite')
parser.add_argument('-i', '--init', action = 'store_true', 
        help = 'Inicia las tablas de la base de datos y les carga artistas y formatos')
args = parser.parse_args()

con = sqlite3.connect(args.file)
cur = con.cursor()

if args.init:
    cur.executescript(open(tables_file).read()) # Defino las tablas

    # Le cargo los diferentes formatos
    formatos = crawler.formatos.items()
    cur.executemany('INSERT INTO formato VALUES (?,?)', formatos)

    # Cargo los artistas
    artistas = crawler.get_artists()
    cur.executemany('INSERT INTO artista(nombre,slug) VALUES (?,?)', artistas)

    con.commit()

notdownloaded = cur.execute('SELECT slug,nombre from artista WHERE descargado=0')
for slug,nombre in notdownloaded.fetchall():
    print 'Descargando canciones de', nombre
    canciones, slugs = crawler.get_canciones(slug)
    for slug_cancion, versiones in canciones.items(): # La clave es el slug
        cur.execute('INSERT INTO cancion VALUES (?,?,?)', (slug, slug_cancion,
            slugs[slug_cancion]))
        for version in versiones:
            cur.execute('INSERT INTO version VALUES (?,?,?,?,?,?)', 
                    (slug_cancion, version['version_id'], version['formato'],
                    version['puntaje'], version['votos'], version['contenido']))
    cur.execute('UPDATE artista SET descargado=1 WHERE slug=?', [slug])
    con.commit()
