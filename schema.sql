drop table if exists users, items, requests, reviews, companies;

create table users (
  id serial primary key,
  nick text unique check(coalesce(nick, '') != ''),
  area int check(area > 18) check(area < 100000),
  contacts text check(coalesce(contacts, '') != ''),
  secret text not null
);

create table items (
  id serial primary key,
  name text check(coalesce(name, '') != ''),
  description text check(coalesce(description, '') != ''),
  link text,
  owner int references users not null,
  possessor int references users,
  removed boolean default false not null
);

create table requests (
  id serial primary key,
  item int references items not null,
  creator int references users not null,
  status text default 'pending' not null
);

create table reviews (
  id serial primary key,
  reviewer int references users not null,
  reviewed int references users not null,
  review int check(review > -2) check(review < 2),
  given timestamp default now() not null
);

create table companies (
  id serial primary key,
  name text unique check(coalesce(name, '') != ''),
  maintainer int references users not null
);
