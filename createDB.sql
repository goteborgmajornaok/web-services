PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "USERS"
(
	ID INTEGER
		primary key autoincrement,
	EVENTOR_PERSON_ID INTEGER not null,
	WORDPRESS_ID INTEGER not null,
	CREATED TEXT NON
, DELETED INTEGER);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('USERS',0);
COMMIT;