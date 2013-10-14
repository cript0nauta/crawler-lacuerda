/*
###############################################################################
# buscador.js                                                                 #
###############################################################################
# JSBuscador de {El Codigo}                                                   #
# Buscador de paginas web realizado con JavaScript                            #
# Version:          JSBuscador 2.0                                            #
# Publicado:        10 de abril de 2007                                       #
# Distribuido por:  http://www.elcodigo.com                                   #
###############################################################################
# Copyright (c) 2007 Ivan Nieto Perez                                         #
# Sujeto a los términos de licencia descritos en el documento licencia.txt    #
# Esta cabecera debe permanecer invariable.                                   #
###############################################################################
*/

//CONFIGURACION
var dominio = 'elcodigo.com'		//dominio desde el que se ejecuta el buscador
var extension = 'html'			//extension de las paginas del site (htm o html)
var pagina_buscador = '/superscripts/jsbuscador/buscador.html'	//ruta y nombre de la pagina de busqueda (con barra por delante)
var imagen_relevancia = 'punt'		//ruta y prefijo nombre de imagenes relevancia (punt_on.gif y punt_off.gif)

var tipo_fuente = 'Verdana, Arial, Serif'
var grosor_fuente = '400'
var color_fuente = '#483713'
var tamano_fuente = '0.9em'

var tamano_fuente_titulo = '1.1em'
var grosor_fuente_titulo = '600'
var color_fuente_titulo = '#A25151'

var color_fondo = '#FAFAF5'

var color_fuente_clave = '#FF0000'

var color_enlace = '#554B8B'
var grosor_enlace = '600'
var color_enlace_visitado = '#AD83B4'
var color_enlace_activo = '#DD0000'
var fondo_enlace_visitado = '#FFA4A4'

var resXpag = 5					//numero de resultados por pagina
var color_subrayado = '#FFFF00'			//color fondo palabra clave subrayada en resultados busqueda
//FIN CONFIGURACION

//NO CAMBIES NADA A PARTIR DE AQUI SI NO SABES LO QUE HACES

//variables globales
var accion
var f = '<p>&nbsp;</p><p>Basado en <a href="http://www.elcodigo.com/superscripts/jsbuscador/jsbuscador.html">JSBuscador 2.0</a><br>de <a href="http://www.elcodigo.com/">{El Codigo}</a></p>'
var h = 465
var g = 664950
var totales			//numero de entradas encontradas
var Pagina = ''		//string que contendra la pagina a mostrar
var resultados = ''	//string reusltados busqueda
var clave2			//palabra a buscar
var res = new Array()	//guarda relevancias busqueda

var caracter = new Object(5) 
caracter[0] = 'á'
caracter[1] = 'é'
caracter[2] = 'í'
caracter[3] = 'ó'
caracter[4] = 'ú'

var caracter_nuevo = new Object(5)
caracter_nuevo[0] = 'a'
caracter_nuevo[1] = 'e'
caracter_nuevo[2] = 'i'
caracter_nuevo[3] = 'o'
caracter_nuevo[4] = 'u'

var caracter_nuevo2 = new Object(5)
caracter_nuevo2[0] = '[áa]'
caracter_nuevo2[1] = '[ée]'
caracter_nuevo2[2] = '[íi]'
caracter_nuevo2[3] = '[óo]'
caracter_nuevo2[4] = '[úu]'

//obtiene longitud de la base de datos
var longitud = BaseDatos.length


function CalculaRelevancia(indice) {

	var CadenasEntrada
	var parciales = 0
	
	//divide la cadena de resultados en subcadenas y escribe los resultados
	CadenasEntrada = BaseDatos[indice].split(";")
	
	//recorre las subcadenas en busca de la clave, para asignar relevancia
	for (var n = 0; n < CadenasEntrada.length; n++) {
		if ( CadenasEntrada[n].search(clave2) != -1 ) {
			parciales++
		}
	}

	if ( parciales != 0 ) {
		res[ res.length ] = parciales + '|' + indice
	}
}

//escribe codigo HTML
function MuestraPagina( htmlData ) {
	if (document.getElementById) {
		document.getElementById("areaDatos").innerHTML = htmlData
	} else if (document.all) {
		document.all["areaDatos"].innerHTML = htmlData
	} else {
		return
	}
}

// lanza proceso busqueda
// nuevaBusqueda = 0	>> buscar
// nuevaBusqueda != 0	>> usar resultados de busqueda anterior
//				   en este caso, nuevaBusqueda tiene el total	
function IniciaBuscador(palabraClave, paginacion, nuevaBusqueda) {
	
	//inicia variables globales
	var desde = 0
	var partes
	var CadenasEntrada
	var descripcion = ''
	totales = nuevaBusqueda		//a 0 si nueva busqueda

	//detiene busqueda si palabra clave vacia
	if ( palabraClave == "" ) {
		alert("¡Introduzca cadena de búsqueda!")
		return
	}
	
	if ( nuevaBusqueda == 0 ) {
	
		//elimina acentos
		var palabra_sin = elimina_especiales(palabraClave)
	
		//obtiene la expresion regular para la busqueda (global e ignorando case)
		clave2 = new RegExp(palabra_sin, "gi")

		//borra array res
		for ( var r=0; r < res.length; r++) {
			res[r]=''
		}

		//busca entrada de pagina que contenga la clave
		//recorre el array en busca de la palabra clave (en cualquier parte)
		for (var x = 0; x < longitud; x++) {
			if ( BaseDatos[x].search(clave2) != -1 ) {
				CalculaRelevancia( x )
				totales++
			}
		}
	
		//ordena resultados segun relevancia
		res.sort( ordenacionNumerica )
	}
	
	//lista de resultados
	resultados = ''
	
	var resfinal = paginacion * resXpag + resXpag
	if ( resfinal >= res.length ) { 
		resfinal = res.length
	}
	
	for ( var n = paginacion * resXpag; n < resfinal; n++) {
		
		partes = res[n].split('|')
		
		resultados += '<tr><td width="70">'
		resultados += MuestraRelevancia( partes[0] )
		
		CadenasEntrada = BaseDatos[ partes[1] ].split(";")
		resultados += '</td><td><a href="' + CadenasEntrada[0] + '.' + extension + '" target="_self">' + CadenasEntrada[1] + '</a>\n'
		descripcion = CadenasEntrada[2]
		descripcion = descripcion.replace( clave2, '<span class="remarcado">' + palabraClave + '</span>')
		resultados += '<br>' + descripcion + '</td></tr>\n'
	}	
	
	//escribe pagina de resultados
	CreaCabecera('<p>Resultados de la búsqueda</p>')

	if (totales != 0)
		Pagina += '<p>Se han encontrado ' + totales + ' resultados que contienen la palabra <b class="clave">' + palabraClave + '</b>:</p>\n'
	else
		Pagina += '<p>No se han encontrado resultados para la palabra <b class="clave">' + palabraClave + '</b>.</p>\n'
	
	Pagina += '<table width="80%">' + resultados + '</table>'
	
	
	
	var sigpag = paginacion + 1
	var antpag = paginacion - 1
	var ultpag = 0
	if ( totales % resXpag  != 0 ) {
		ultpag = Math.floor(totales / resXpag)
	} else {
		ultpag = totales / resXpag - 1
	}
	
	if ( ultpag > 0 ) {				//si hay que paginar
		Pagina += '<p>Pagina de resultados: '
	}
	
	if ( paginacion > 0  ) {			//si no estamos en la primera pagina
		Pagina += '<a href="javascript: IniciaBuscador(\'' + palabraClave + '\', ' + antpag + ', ' + totales + ')">Anterior</a> '
	}
	
	if ( ultpag > 0 ) {
		for ( var r = 0; r <= ultpag; r++ ) {	//lista todas las paginas
			if ( r != paginacion ) {
				Pagina += ' <a href="javascript: IniciaBuscador(\'' + palabraClave + '\', ' + r + ', ' + totales + ')">' + r + '</a> '
			} else {
				Pagina += ' ' + r + ' '
			}
		}
	}
	
	if ( paginacion < ultpag ) {			//si no estamos en la ultima pagina
		Pagina += ' <a href="javascript: IniciaBuscador(\'' + palabraClave + '\', ' + sigpag + ', ' + totales + ')">Siguiente</a></p>'
	} else {
		Pagina += '</p>'
	}
	
	Pagina += '<p><a href="http://' + dominio + pagina_buscador + '">Nueva búsqueda</a></p>'
	CreaPie()

	//escribe los resultados
	MuestraPagina(Pagina)
}

//SUSTITUYE TODAS LAS OCURRENCIAS DE UN CARACTER UNA CADENA POR OTRO CARACTER
function sustituye_caracter(cadena, caracter, nuevo_caracter) {
	var longitud, indice 
 	
  	longitud = cadena.length
  	indice = cadena.indexOf(caracter)
  	while ( (indice != -1) && (cadena.charAt(indice + 1) != ']') ) {
     		cadena = cadena.substring(0, indice) + nuevo_caracter + cadena.substring(indice + 1, longitud + 1)
      		indice = cadena.indexOf(caracter, indice)
      	}

	return cadena
}

//ELIMINA CARACTERES ESPECIALES
function elimina_especiales(cadena) {

	//elimina caracteres con acento
	for (x = 0; x < 5; x++) {
		cadena = sustituye_caracter(cadena, caracter[x], caracter_nuevo[x])
   	}
   	
	//sustituye las vocales por una expresion regular para ignorar los acentos
	for (x = 0; x < 5; x++) {
		cadena = sustituye_caracter(cadena, caracter_nuevo[x], caracter_nuevo2[x])
   	}   	
	
	return cadena
}

//MUESTRA IMAGENES DE RELEVANCIA
function MuestraRelevancia(relevancia) {

	var cadena_relevancia = ''
	
	for (var x = 0; x < relevancia; x++) cadena_relevancia += '<img src="' + imagen_relevancia + '_on.gif" width="15" height="16" border="0">'
 	for (var y = 0; y < 4 - relevancia; y++) cadena_relevancia += '<img src="' + imagen_relevancia + '_off.gif" width="15" height="16" border="0">'
 	
 	return cadena_relevancia 
}

//MUESTRA FORMULARIO DE BUSQUEDA
function MuestraBuscador() {
				 if ( cdfcr( f, h ) == g ) { accion = 'verform';	CreaBuscador();	MuestraPagina( Pagina ); }
}

function CreaBuscador() {

	//inicia variables globales
	CreaCabecera( '<p>Introduzca una palabra clave y pulse el botón <b>Buscar</b>.</p>' )

	Pagina += '<form name="FormularioBusqueda">\n' +
		'<p><small>Palabra clave:</small><br>\n' +
		'<input type="text" name="palabra" size="25">\n' +
		'<input type="hidden" name="pagina" value="0">\n' +
		'<input type="button" value="Buscar" name="buscar" onClick="IniciaBuscador(this.form.palabra.value, this.form.pagina.value, 0)">\n' +
		'<input type="reset" value="Borrar" name="borrar"></p></form>\n'
		
	CreaPie()		
}

//codigo de inicio de pagina
function CreaCabecera( texto ) {
	Pagina = ""
	//crea inicio pagina a visualizar y la muestra
	Pagina += texto
}

//codigo de fin de pagina
function CreaPie() {
	//crea final pagina
//	if ( accion != 'verenl' ) Pagina += '<p><a href="' + url_album + '">Inicio</a></p>\n'
	Pagina += f
}

//MUESTRA ESTILOS
function MuestraEstilos() {
	document.write(	'<style type="text/css">\n' +
		'body {font-family: ' + tipo_fuente + '; font-weight: ' + grosor_fuente + '; color: ' + color_fuente + '; background-color: ' + color_fondo + '; }\n' +
		'.clave {color: ' + color_fuente_clave + ';}\n' +
		'a:link {color: ' + color_enlace + '; text-decoration: none; font-weight: ' + grosor_enlace + ';}\n' +
		'a:visited {color: ' + color_enlace_visitado + '; text-decoration: none; font-weight: ' + grosor_enlace + ';}\n' +
		'a:active {color: ' + color_enlace_activo + '; text-decoration: none; font-weight: ' + grosor_enlace + ';}\n' +
		'a:hover {color: ' + color_enlace + '; text-decoration: none;background: ' + fondo_enlace_visitado + '; font-weight: ' + grosor_enlace + ';}\n' +
		'td  { padding: 7px;  font-size: ' + tamano_fuente + '; vertical-align: top; }\n' +
		'table { margin-left: 50px; margin-right: 50px;}\n' +
		'h1 {margin-left: 25px; margin-right: 20px; font-size: ' + tamano_fuente_titulo + '; font-weight: ' + grosor_fuente_titulo + '; color: ' + color_fuente_titulo + ';}\n' +
		'p {margin-left: 25px; margin-right: 20px; font-size: ' + tamano_fuente + ';}\n' +
		'.remarcado {background:' + color_subrayado + ';}\n' +
		'</style>\n' )

}

//check
function cdfcr(a, b) {
	var alfa= 'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHI123456789'
	var d = 0
	var palabra = a.toUpperCase()
	for (var i=0; i< palabra.length; i++) {
		letra = palabra.substring(i,i+1)
		c = alfa.indexOf(letra, 0) + 1
		d = d + b * c
	}
	return d
}

function ordenacionNumerica(a,b) {
	var a2 = a.split('|')
	var b2 = b.split('|')
	return b2[0] - a2[0]
}
