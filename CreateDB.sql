CREATE DATABASE PayAttentionTickers;

DROP TABLE public.users;
CREATE TABLE public.users
(
	user_id varchar(32) NOT NULL,
	alarm boolean NOT NULL,
	alarm_limit integer DEFAULT 0,
	user_pwd text,
	token text,
	token_exp timestamp without time zone,
	CONSTRAINT pk_user_id PRIMARY KEY (user_id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.users
    OWNER to pi;

DROP TABLE public.tickers;
CREATE TABLE public.tickers
(
	key_id serial NOT NULL,
	user_id varchar(32) REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,
	ticker_id varchar(16) NOT NULL,
	ticker_desc text,
	deviat_month real,
	deviat_week real,
	update_date timestamp without time zone,
	CONSTRAINT pk_key_id PRIMARY KEY (key_id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.tickers
    OWNER to pi;

DROP TABLE public.logs;
CREATE TABLE public.logs
(
	log_id serial NOT NULL,
	date timestamp without time zone NOT NULL,
	user_id varchar(32) REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,
	message text,
	CONSTRAINT pk_log_id PRIMARY KEY (log_id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.logs
    OWNER to pi;


DROP TABLE public.stock_exchange;
CREATE TABLE public.stock_exchange
(
    ticker_id character varying(16) NOT NULL,
    ticker_desc text,
    PRIMARY KEY (ticket_id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.stock_exchange
    OWNER to pi;
