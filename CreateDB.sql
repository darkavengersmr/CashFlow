CREATE DATABASE cashflow;

CREATE TABLE public.users
(
	id serial NOT NULL,
	username text NOT NULL,
	email text  NOT NULL,
	hashed_password text,
	is_active boolean NOT NULL,
	CONSTRAINT pk_users_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.users
    OWNER to pi;


CREATE TABLE public.inflow
(
	id serial NOT NULL,
	date timestamp without time zone,
	description text NOT NULL,
	sum integer,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_inflow_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.inflow
    OWNER to pi;


CREATE TABLE public.inflow_regular
(
	id serial NOT NULL,
	description text NOT NULL,
	sum integer,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_inflow_regular_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.inflow_regular
    OWNER to pi;


CREATE TABLE public.outflow
(
	id serial NOT NULL,
	date timestamp without time zone,
	description text NOT NULL,
	sum integer,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_outflow_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.outflow
    OWNER to pi;


CREATE TABLE public.outflow_regular
(
	id serial NOT NULL,
	description text NOT NULL,
	sum integer,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_outflow_regular_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.outflow_regular
    OWNER to pi;


CREATE TABLE public.assets
(
	id serial NOT NULL,
	date_in timestamp without time zone,
	date_out timestamp without time zone,
	description text NOT NULL,
	sum integer,
	category_id integer REFERENCES categories(id) ON DELETE CASCADE,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,	
	CONSTRAINT pk_assets_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.assets
    OWNER to pi;


CREATE TABLE public.liabilities
(
	id serial NOT NULL,
	date_in timestamp without time zone,
	date_out timestamp without time zone,
	description text NOT NULL,
	sum integer,
	category_id integer REFERENCES categories(id) ON DELETE CASCADE,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_liabilities_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.liabilities
    OWNER to pi;


CREATE TABLE public.categories
(
	id serial NOT NULL,
	category text NOT NULL,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_categories_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.categories
    OWNER to pi;


CREATE VIEW public.inflow_lastsum
 AS
 SELECT inflow.description,
    inflow.sum,
    inflow.owner_id
   FROM inflow
  WHERE inflow.date = ( SELECT max(inflow_1.date) AS max
           FROM inflow inflow_1
          WHERE inflow_1.description = inflow.description and inflow.owner_id = inflow_1.owner_id);

ALTER TABLE public.inflow_lastsum
    OWNER TO pi;


CREATE VIEW public.outflow_lastsum
 AS
 SELECT outflow.description,
    outflow.sum,
    outflow.owner_id
   FROM outflow
  WHERE outflow.date = ( SELECT max(outflow_1.date) AS max
           FROM outflow outflow_1
          WHERE outflow_1.description = outflow.description and outflow.owner_id = outflow_1.owner_id);

ALTER TABLE public.outflow_lastsum
    OWNER TO pi;
