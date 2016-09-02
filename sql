create table 2dcode( id int auto_increment primary key not null, 2did varchar(200), picurl varchar(200), type int not null default 0 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
create table spread( id int primary key not null, name varchar(20), count int default 0, FOREIGN KEY (id) REFERENCES 2dcode(id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;
create table friends( id int primary key not null, name varchar(20), picurl varchar(200), description text, count int default 0, FOREIGN KEY (id) REFERENCES 2dcode(id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;
