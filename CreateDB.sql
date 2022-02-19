CREATE DATABASE cashflow;

DROP TABLE public.users;
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

DROP TABLE public.inflow;
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


DROP TABLE public.outflow;
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


DROP TABLE public.outflow_regular;
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


DROP TABLE public.assets;
CREATE TABLE public.assets
(
	id serial NOT NULL,
	date_in timestamp without time zone,
	date_out timestamp without time zone,
	description text NOT NULL,
	sum integer,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_assets_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.assets
    OWNER to pi;


DROP TABLE public.liabilities;
CREATE TABLE public.liabilities
(
	id serial NOT NULL,
	date_in timestamp without time zone,
	date_out timestamp without time zone,
	description text NOT NULL,
	sum integer,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_liabilities_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.liabilities
    OWNER to pi;
 
