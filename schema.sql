create table users (
  id serial primary key,
  nick text,
  area int,
  contacts text,
  secret text
);

create table items (
  id serial primary key,
  name text,
  description text,
  link text,
  owner int references users,
  possessor int references users
);
