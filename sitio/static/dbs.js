var BaseDatos = new Array();
function add_db(path, titulo, descripcion, tags)
{
    /* Añade a la base de datos de búsqueda el elemento indicado */
    tags = tags.join(','); // tag1,tag2,tag3,tagN
    obj = [path, titulo, descripcion, tags].join(';');
    BaseDatos.push(obj);
    longitud = BaseDatos.length; // Sino no va a funcionar
}
$(function(){
    $.getJSON('/db.json', function(data){
        artistas = data['artistas'];
        canciones = data['canciones'];
        $.each(artistas, function(key, value){
            nombre = value;
            slug = key;
            descripcion = 'Canciones del artista ' + nombre;
            add_db('/'+slug, nombre, descripcion, ['artista']);
        });
        $.each(canciones, function(key, value){
            for(i=0; i<value.length; i++)
            {
                slug_artista = key;
                artista = artistas[slug_artista];
                slug_cancion = value[i].s;
                titulo = value[i].t;
                descripcion = 'Autor: ' + artista;
                url = '/' + slug_artista + '/' + slug_cancion;
                add_db(url, titulo, descripcion, ['cancion']);
            }
        });
    });
})
