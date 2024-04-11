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

create table requests (
  id serial primary key,
  item int references items,
  creator int references users,
  status text default 'pending'
);

create table reviews (
  id serial primary key,
  reviewer int references users,
  reviewed int references users,
  review int,
  given timestamp default now()
);
