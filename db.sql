CREATE table artista (
    slug VARCHAR(100) PRIMARY KEY NOT NULL UNIQUE,
    nombre VARCHAR(100),
    descargado boolean default 0
);

create table cancion (
    slug_artista VARCHAR(100),
    slug VARCHAR(100), 
    titulo VARCHAR(100),
    PRIMARY KEY (slug_artista, slug),
    FOREIGN KEY(slug_artista) REFERENCES artista(slug)
);

create table formato (
    id char(1) PRIMARY KEY, -- identificador de una letra
    descripcion varchar(50)
);

create table version (
    id_cancion integer,
    version tinyint,
    formato char(1),
    puntaje float,
    votos integer,
    contenido text,
    PRIMARY KEY (id_cancion, version),
    FOREIGN KEY(id_cancion) REFERENCES cancion(rowid),
    FOREIGN KEY(formato) REFERENCES formato(id)
);

