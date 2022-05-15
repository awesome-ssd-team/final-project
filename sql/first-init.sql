CREATE SCHEMA public;

CREATE SCHEMA secured;

CREATE SCHEMA backend;

CREATE TABLE public.users (
	created_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	updated_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	user_id              INT UNSIGNED NOT NULL    PRIMARY KEY,
	password             BLOB  NOT NULL    ,
	full_name            BLOB  NOT NULL    ,
	email                BLOB  NOT NULL    ,
	secondary_password   BLOB  NOT NULL
 );

CREATE TABLE public.user_login_logs (
	attempt_id           INT UNSIGNED NOT NULL  AUTO_INCREMENT  PRIMARY KEY,
	user_id              INT UNSIGNED NOT NULL    ,
	session_id           VARCHAR(150)  NOT NULL    ,
	session_start_at     TIMESTAMP  NOT NULL    ,
	session_expired_at   TIMESTAMP  NOT NULL    ,
	created_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	CONSTRAINT idx_user_login_logs_0 UNIQUE ( session_id )
 ) engine=InnoDB;

CREATE TABLE public.blocked_session (
	block_id             INT UNSIGNED NOT NULL  AUTO_INCREMENT  PRIMARY KEY,
	session_id           VARCHAR(150)  NOT NULL    ,
	blocked_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	blocked_until        TIMESTAMP  NOT NULL    ,
	created_at           TIMESTAMP  NOT NULL DEFAULT (now())
 ) engine=InnoDB;

CREATE TABLE secured.users (
	user_id              INT UNSIGNED NOT NULL  AUTO_INCREMENT  PRIMARY KEY,
	created_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	updated_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	password             VARCHAR(16)  NOT NULL    ,
	full_name            VARCHAR(100)  NOT NULL    ,
	email                TEXT  NOT NULL    ,
	secondary_password   VARCHAR(6)  NOT NULL
 ) engine=InnoDB;

CREATE INDEX fk_user_login_logs ON public.user_login_logs ( user_id );

ALTER TABLE public.blocked_session ADD CONSTRAINT fk_blocked_session FOREIGN KEY ( session_id ) REFERENCES public.user_login_logs( session_id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE public.user_login_logs ADD CONSTRAINT fk_user_login_logs FOREIGN KEY ( user_id ) REFERENCES public.users( user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

CREATE TRIGGER secured.user_table_insert AFTER INSERT ON users FOR EACH ROW BEGIN
        SET @encryption_key = NEW.secondary_password;
        INSERT INTO public.users (user_id, password, secondary_password, email, full_name)
        VALUES(
               NEW.user_id,
               MD5(NEW.password),
               MD5(NEW.secondary_password),
               AES_ENCRYPT(NEW.email, @encryption_key),
               AES_ENCRYPT(NEW.full_name, @encryption_key)
        );
    END;

CREATE TRIGGER secured.user_table_update AFTER UPDATE ON users FOR EACH ROW BEGIN
        SET @encryption_key = NEW.secondary_password;
        UPDATE public.users
        SET
            full_name = AES_ENCRYPT(NEW.full_name, @encryption_key),
            email = AES_ENCRYPT(NEW.email, @encryption_key),
            password = MD5(NEW.password),
            secondary_password = MD5(secondary_password)
        WHERE user_id = NEW.user_id;
    END;
