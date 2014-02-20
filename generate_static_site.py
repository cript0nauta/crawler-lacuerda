#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sqlite3
import argparse
import json
from progressbar import ProgressBar
from jinja2 import Environment, PackageLoader
from pyquery import PyQuery as P
from crawler import get_pq

PATH = '/'

default_out = os.path.join(os.path.dirname(__file__), 'sitio/')
default_db = os.path.join(os.path.dirname(__file__), 'db.db')

parser = argparse.ArgumentParser(description='Genera el sitio estático')
parser.add_argument('-f', '--db-file', default = default_db, help = 'Fichero SQLite')
parser.add_argument('-o', '--output', default = default_out, help = 'Directorio de salida del json. Por defecto %s' % default_out)

args = parser.parse_args()

con = sqlite3.connect(args.db_file)
con.row_factory = sqlite3.Row # Puedo ver los resultados de consultas como dict
cur = con.cursor()
env = Environment(loader=PackageLoader('templates','.'))

# Genero un JSON con los nombres y slugs de artistas
print 'Generando JSON de artistas...'
artistas = dict()
for slug, nombre in cur.execute("""
        SELECT slug, nombre FROM artista"""):
    artistas[nombre] = slug
f = open(args.output + '/artistas.json', 'w')
json.dump(artistas, f)
f.close()


# Genero el index
print 'Generando index.html....'
pq = get_pq('/')
pq_artpop = pq('.cPop li a em').parent()
pq_artpop.find('em').text('') # borro el tabs

# Artistas populares
artpop = []
for e in pq_artpop:
    artista = P(e)
    split = artista.attr('href').split('/')
    slug = split[-1] or split[-2] # Por la barra al final
    nombre = artista.text()
    artpop.append((slug, nombre))

# Canciones populares
pq_cpop = pq('.cPop a i').parent()
cpop = []
for e in pq_cpop:
    cancion = P(e)
    nombre_artista = cancion.find('i').text()
    cancion.find('i').text('') 
    titulo = cancion.text()[:-1] # Saco la coma al final
    href = cancion.attr('href')
    slug_artista, slug_cancion = href.split('/')[-2:]
    cpop.append((titulo, slug_cancion, slug_artista, nombre_artista))

f = open(os.path.join(args.output, 'index.html'), 'w')
template_index = env.get_template('index.html')
render = template_index.render(path = PATH, cpop = cpop, artpop = artpop)
f.write(render.encode('utf8'))
f.close()


# Genero HTMLs para los artistas
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

    render = template_artista.render(path = PATH, nombre = nombre, slug = slug, 
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
             versiones = versiones,
             path = PATH
             )

     f = open(os.path.join(args.output, 'artistas', c['slug_artista'], 
         c['slug_cancion'] + '.html'), 'w')
     f.write(render.encode('utf8'))
     f.close()
     pbar.update(c['rowid'])


total_versiones = cur.execute('SELECT count(*) FROM version').fetchone()[0]
pbar = ProgressBar(maxval = total_versiones)
pbar.widgets.insert(0, 'Generando TXTs para las versiones ... ')
q = """
select
	a.slug as slug_artista,
    contenido,
	(c.slug || '-' || version || '.txt') as filename
from version
join cancion as c on
	c.rowid = id_cancion
join artista as a on
	c.slug_artista = a.slug
"""
for version in pbar(cur.execute(q)):
    f = open(os.path.join(args.output, 'artistas', version['slug_artista'],
        version['filename']), 'w')
    f.write(version['contenido'].encode('utf8'))
    f.close()
