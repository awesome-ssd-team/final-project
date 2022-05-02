CREATE SCHEMA ssd_backend;

CREATE TABLE ssd_backend.session_logs (
	session_id           INT UNSIGNED NOT NULL  AUTO_INCREMENT  PRIMARY KEY,
	created_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	expired_at           TIMESTAMP  NOT NULL
 ) engine=InnoDB;

CREATE TABLE ssd_backend.`user` (
	user_id              INT UNSIGNED NOT NULL  AUTO_INCREMENT  PRIMARY KEY,
	name                 VARCHAR(100)  NOT NULL    ,
	email                VARCHAR(100)  NOT NULL    ,
	password             TEXT  NOT NULL    ,
	created_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	updated_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	identity_number      VARBINARY(500)      ,
	address              VARBINARY(500)
 ) engine=InnoDB;

CREATE TABLE ssd_backend.user_logs (
	attempt_id           INT UNSIGNED NOT NULL  AUTO_INCREMENT  PRIMARY KEY,
	session_id           INT UNSIGNED NOT NULL    ,
	session_start        TIMESTAMP  NOT NULL    ,
	user_id              INT UNSIGNED NOT NULL    ,
	created_at           TIMESTAMP  NOT NULL DEFAULT (now())   ,
	CONSTRAINT fk_user_logs_user FOREIGN KEY ( user_id ) REFERENCES ssd_backend.`user`( user_id ) ON DELETE NO ACTION ON UPDATE CASCADE,
	CONSTRAINT fk_user_logs_session_log FOREIGN KEY ( session_id ) REFERENCES ssd_backend.session_logs( session_id ) ON DELETE NO ACTION ON UPDATE CASCADE
 ) engine=InnoDB;

CREATE INDEX idx_user_logs ON ssd_backend.user_logs ( user_id );

CREATE INDEX fk_user_logs_session_log ON ssd_backend.user_logs ( session_id );

CREATE TRIGGER ssd_backend.encrypt_password_update BEFORE UPDATE ON user FOR EACH ROW SET NEW.password = MD5(OLD.password);

CREATE TRIGGER ssd_backend.hash_password_insert BEFORE INSERT ON user FOR EACH ROW SET NEW.password = MD5(NEW.password);

CREATE TRIGGER ssd_backend.hash_password_update BEFORE UPDATE ON user FOR EACH ROW SET NEW.password = MD5(OLD.password);

/* NEED FURTHER EXPLORATION */
-- CREATE TRIGGER ssd_backend.protect_sensitive_information_insert BEFORE INSERT ON user FOR EACH ROW BEGIN
--         SET @encryption_key = MD5(NEW.password);
--         SET NEW.identity_number = AES_ENCRYPT(NEW.identity_number, @encryption_key),
--             NEW.address = AES_ENCRYPT(NEW.address, @encryption_key);
--     END;
--
-- CREATE TRIGGER ssd_backend.protect_sensitive_information_update BEFORE UPDATE ON user FOR EACH ROW BEGIN
--         SET @encryption_key = NULL;
--         SELECT password INTO @encryption_key FROM ssd_backend.user WHERE user_id = NEW.user_id;
--         SET NEW.identity_number = AES_ENCRYPT(NEW.identity_number, @encryption_key),
--             NEW.address = AES_ENCRYPT(NEW.address, @encryption_key);
--     END;

-- /* ------ ADMINS ------ */
--
-- CREATE USER ssd_admin WITH PASSWORD 'ssd_admin';
-- GRANT CONNECT ON DATABASE backend TO ssd_admin;
--
-- -- PUBLIC
-- GRANT USAGE ON SCHEMA public TO ssd_admin;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ssd_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public
--    GRANT ALL PRIVILEGES ON TABLES TO ssd_admin;
--
-- -- SECURED
-- GRANT USAGE ON SCHEMA secured TO ssd_admin;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA secured TO ssd_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA secured
--    GRANT ALL PRIVILEGES ON TABLES TO ssd_admin;
--
--
-- /* ------ USERS ------ */
--
-- CREATE USER ssd_user WITH PASSWORD 'ssd_user';
-- GRANT CONNECT ON DATABASE backend TO ssd_user;
--
-- -- PUBLIC
-- GRANT USAGE ON SCHEMA public TO ssd_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO ssd_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public
--    GRANT SELECT ON TABLES TO ssd_user;
--
-- -- -- SECURED
-- -- GRANT USAGE ON SCHEMA secured TO ssd_admin;
-- -- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA secured TO ssd_admin;
-- -- ALTER DEFAULT PRIVILEGES IN SCHEMA secured
-- --    GRANT ALL PRIVILEGES ON TABLES TO ssd_admin;
