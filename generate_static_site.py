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

parser = argparse.ArgumentParser(description='Genera el sitio estático')
parser.add_argument('-f', '--db-file', default = default_db, help = 'Fichero SQLite')
parser.add_argument('-o', '--output', default = default_out, help = 'Directorio de salida del json. Por defecto %s' % default_out)

args = parser.parse_args()

con = sqlite3.connect(args.db_file)
con.row_factory = sqlite3.Row # Puedo ver los resultados de consultas como dict
cur = con.cursor()

# Genero un JSON con los nombres y slugs de artistas
print 'Generando JSON de artistas...'
artistas = dict()
for slug, nombre in cur.execute("""
        SELECT slug, nombre FROM artista"""):
    artistas[nombre] = slug
f = open(args.output + '/artistas.json', 'w')
json.dump(artistas, f)
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

pbar = ProgressBar()
pbar.widgets.insert(0, 'Generando HTMLs para las canciones ... ')
q = """
    select
        c.rowid,
        a.slug as slug_artista,
        a.nombre as artista,
        c.slug as slug_cancion,
        titulo as titulo_cancion
    from cancion as c
    join artista as a on
        slug_artista = a.slug
"""
template_cancion = env.get_template('cancion.html')
for c in pbar(cur.execute(q).fetchall()):
     versiones = []
     q_ = """
        select
            version,
            formato as id_formato,
            f.descripcion as formato,
            puntaje,
            votos
        from version
        join formato as f on
            formato = f.id
        where id_cancion=?
        """
     for v in cur.execute(q_, [c['rowid']]):
         versiones.append(dict(
             version = v['version'],
             formato = v['formato'],
             puntaje = v['puntaje'],
             votos   = v['votos'],
             ))

     render = template_cancion.render(slug_artista = c['slug_artista'],
             nombre_artista = c['artista'],
             slug_cancion = c['slug_cancion'],
             titulo = c['titulo_cancion'],
             versiones = versiones             
             )

     f = open(os.path.join(args.output, 'artistas', c['slug_artista'], 
         c['slug_cancion'] + '.html'), 'w')
     f.write(render.encode('utf8'))
     f.close()
     pbar.update(c['rowid'])


template_version = env.get_template('version.html')
total_versiones = cur.execute('SELECT count(*) FROM version').fetchone()[0]
pbar = ProgressBar(maxval = total_versiones)
pbar.widgets.insert(0, 'Generando HTMLs para las versiones ... ')
q = """
select
	a.slug as slug_artista,
	a.nombre as nombre_artista,
	c.slug as slug_cancion,
	c.titulo,
	version,
	formato as id_formato,
	f.descripcion as formato,
	puntaje,
	votos,
    contenido,
	(c.slug || '-' || version || '.html') as filename
from version
join cancion as c on
	c.rowid = id_cancion
join artista as a on
	c.slug_artista = a.slug
join formato as f on
	formato = f.id
"""
for version in pbar(cur.execute(q)):
    render = template_version.render(**version)
    f = open(os.path.join(args.output, 'artistas', version['slug_artista'],
        version['filename']), 'w')
    f.write(render.encode('utf8'))
    f.close()
