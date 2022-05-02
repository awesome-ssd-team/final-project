/* AUTO ENCRYPT SENSITIVE INFORMATION */

/* HASH PASSWORD */
DROP TRIGGER IF EXISTS encrypt_password_insert;
DROP TRIGGER IF EXISTS hash_password_update;
CREATE TRIGGER hash_password_update
    BEFORE UPDATE ON ssd_backend.user
    FOR EACH ROW
SET NEW.password = CAST(MD5(OLD.password) AS CHAR(250));

DROP TRIGGER IF EXISTS encrypt_password_insert;
DROP TRIGGER IF EXISTS hash_password_insert;
CREATE TRIGGER hash_password_insert
    BEFORE INSERT ON ssd_backend.user
    FOR EACH ROW
SET NEW.password = CAST(MD5(NEW.password) AS CHAR(250));


/* MASKS SENSITIVE INFORMATION */
DROP TRIGGER IF EXISTS protect_sensitive_information_update;
CREATE TRIGGER protect_sensitive_information_update
BEFORE UPDATE ON ssd_backend.user
FOR EACH ROW FOLLOWS hash_password_update
    BEGIN
        SET @encryption_key = NULL;

        SELECT password INTO @encryption_key FROM ssd_backend.user WHERE user_id = NEW.user_id;

        SET NEW.identity_number = AES_ENCRYPT(NEW.identity_number, @encryption_key),
            NEW.address = AES_ENCRYPT(NEW.address, @encryption_key);
    END;


DROP TRIGGER IF EXISTS protect_sensitive_information_insert;
CREATE TRIGGER protect_sensitive_information_insert
BEFORE INSERT ON ssd_backend.user
FOR EACH ROW FOLLOWS hash_password_insert
    BEGIN
        SET @encryption_key = CAST(MD5(NEW.password) AS CHAR(250));

        SET NEW.identity_number = AES_ENCRYPT(NEW.identity_number, @encryption_key),
            NEW.address = AES_ENCRYPT(NEW.address, @encryption_key);
    END;