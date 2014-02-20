#-*- coding: utf-8 -*-

import requests
import spidermonkey
from urlparse import urljoin
from pyquery import PyQuery as P
import time

HOST = 'http://acordes.lacuerda.net/'
verbose = True

formatos = {
        'R' : 'Acordes',
        'K' : 'Piano',
        'T' : 'Tablatura para guitarra',
        'H' : u'Armónica',
        'B' : 'Bajo',
        'D' : u'Batería'
        }

def get_pq(path, base=HOST):
    """ Retorna un objeto PyQuery a partir de un path a la página de
    lacuerda. El argumento opcional base indica la URL a la que se le
    agrega el path"""
    try:
        return P(requests.get(urljoin(base, path)).text)
    except requests.exceptions.ConnectionError:
        print 'Conexión rehusada. Reintentando en 20 segundos'
        time.sleep(20)
        return P(requests.get(urljoin(base, path)).text)

def get_artists():
    """ Devuelve una lista con tuplas de Nombre e identificador 
    único del artista"""

    artistas = []
    slugs = [] # Para que no se repitan si aparecen dos veves

    #Obtengo el menú con las iniciales de los artistas
    pq = get_pq('/tabs/')
    for link in pq('#a_menu td a'):
        link = P(link)
        url = link.attr('href')
        letra = link.text()
        if verbose: print 'Explorando la letra', letra
        
        # Obtengo las URL para cada página de cada letra
        pq_letra = get_pq(url)
        for link in pq_letra('.multipag a'):
            link = P(link)
            texto = link.text()
            url_pag = link.attr('href')
            #if verbose: print '\tExplorando la página', texto
            pq_pagina = get_pq(url_pag, urljoin(HOST, url))
            #Obtengo los artistas de esa página
            for artista in pq_pagina('#i_main li a'):
                artista = P(artista)
                nombre = artista.text()
                nombre = ' '.join(nombre.split()[2:]) # Elimino el Canciones de
                id_artista = artista.attr('href')
                id_artista = id_artista[1:-1] # Le saco las /
                if not id_artista in slugs:
                    artistas.append((nombre, id_artista))
                slugs.append(id_artista)

    return artistas


rt = spidermonkey.Runtime()
cx = rt.new_context()
def get_canciones(artista):
    """ Devuelve un diccionario con listas con diferentes versiones para
    cada canción y otro para el título correspondiente a cada slug """

    canciones = dict()
    slugs = dict()

    pq = get_pq(artista) # La página del artista
    for cancion in pq('#b_main li a'):
        cancion = P(cancion)
        slug = cancion.attr('href')
        titulo = cancion.text()
        titulo = ' '.join(titulo.split()[:-1])
        slugs[slug] = titulo
        if verbose: print '\tCargando canción', titulo
        pq_versiones = get_pq(artista + '/' + slug)

        #Busco el PHP que tiene los matadatos de las versiones
        cal_url = None
        for script in pq_versiones('script[src]'):
            src = P(script).attr('src')
            if 'cal.php' in src:
                cal_url = src
                break

        #Ejecuto el javascript del cal.php
        cal_url = urljoin(HOST, cal_url)
        try:
            cal = requests.get(cal_url).text
        except requests.exceptions.ConnectionError:
            print 'Error de conexión. Reintentando en 20 segundos'
            time.sleep(20)
            cal = requests.get(cal_url).text
        cal = cal[cal.find('trcal'):] # A veces el JS tiene warnings de PHP
        cx.execute(cal)
        metadata = list(cx.execute('trcal'))

        # Descargo todas las versiones para la canción
        versiones = []
        for tr_version in pq_versiones('#r_main tr[onclick]'):
            tr_version = P(tr_version)
            version_id = int(tr_version.attr('onclick')[2])
            slug_version = slug
            if version_id != 1:
                slug_version += '-' + str(version_id)
            metadata_version = metadata[version_id]
            if not metadata_version: # Hay algunos errores 404 que debo ignorar
                print 'Canción inexistente. Ignorando'
                continue
            formato, puntaje, votos = metadata_version
            url_letra = urljoin(HOST, '/'.join(['TXT', artista, 
                slug_version+'.txt']))
            try:
                letra = requests.get(url_letra).text
            except requests.exceptions.ConnectionError:
                print 'Error de conexión. Reintentando en 20 segundos'
                time.sleep(20)
                letra = requests.get(url_letra).text
            version = dict(
                    version_id = version_id,
                    slug = slug_version,
                    formato = formato,
                    puntaje = puntaje,
                    votos = votos,
                    contenido = letra)
            versiones.append(version)

        canciones[slug] = versiones

    return canciones, slugs
