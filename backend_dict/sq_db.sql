create table if not exists mainmenu (
id integer primary key autoincrement,
title text not null,
url text not null
);

CREATE TABLE IF NOT EXISTS posts (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS mfk (
id integer PRIMARY KEY AUTOINCREMENT,
name text,
faculty text,
online text,
openclose text,
score text
);


CREATE TABLE IF NOT EXISTS comments (
id integer PRIMARY KEY AUTOINCREMENT,
username text,
text text,
mfkname text,
score text
);

--name text,
--faculty text,
--online text,
--openclose text,
--discribe text,
--teachers text,
--whereis text,
--whenis text,
--complexity text,
--semester text,
--record text,
--score text,
--url text,