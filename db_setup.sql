DROP TABLE IF EXISTS public.item CASCADE;
DROP TABLE IF EXISTS public.category CASCADE;

CREATE TABLE public.category (
  id serial PRIMARY KEY NOT NULL,
  name varchar(80) NOT NULL,
  description varchar(250) NOT NULL
);


CREATE TABLE public.item (
  id serial PRIMARY KEY NOT NULL,
  name varchar(80) NOT NULL,
  description varchar(250) NOT NULL,
  category_id int NOT NULL REFERENCES category(id),
  date_insert date NOT NULL
);

Insert into public.category (name, description) values ('E-cigarettes','Vaping stuff');
Insert into public.category (name, description) values ('Consoles','Play stuff');

Insert into public.item (name, description, category_id, date_insert) values ('Pico squeeze by Eleaf', 'compact mech mod bottom feeder', 1, '2017-06-13');
Insert into public.item (name, description, category_id, date_insert) values ('Kangertech dripbox 160w', 'VW mod bottom feeder', 1, '2017-06-13');
Insert into public.item (name, description, category_id, date_insert) values ('MS Xbox one s', '4k video by Microsoft', 2, '2017-06-13');
Insert into public.item (name, description, category_id, date_insert) values ('PS4 Pro', 'PC style personalization by Sony', 2, '2017-06-13');
