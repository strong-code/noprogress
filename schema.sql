drop table if exists users;
create table users (
	userid integer primary key autoincrement,
	username string not null,
	password string not null,
	email string not null
);