drop table if exists users;
drop table if exists entries;
create table users (
    userid text primary key,
    password text not null
);
create table entries (
    seat integer primary key,
    train text not null,
    empty integer not null
);
