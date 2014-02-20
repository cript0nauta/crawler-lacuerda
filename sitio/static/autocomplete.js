$(function(){
      $.getJSON(path + 'artistas.json', function(data){
          artistas = data;
          keys=[];
          for (var k in data) keys.push(k);
          $('#txtbusca').autocomplete({
                    source: keys,
                    select: function(evt,ui){
                        nombre = ui.item.value;
                        slug = artistas[nombre];
                        document.location.href = path + 'artistas/' + slug;
                    }
                });
          }
          )});

