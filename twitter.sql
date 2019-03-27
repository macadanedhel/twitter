-- Drop table
DROP TABLE twitter.tusers
-- DROP TABLE twitter.tusers

CREATE TABLE twitter.tusers (
	"_id" int8 NOT NULL,
	"name" varchar NOT NULL,
	screen_name varchar NOT NULL,
	created_at timestamptz NULL,
	lang varchar NULL,
	"current" bool NULL DEFAULT true,
	verified bool NULL DEFAULT false,
	description varchar NULL,
	location varchar NULL,
	utc_offset int4 NULL,
	active bool NOT NULL DEFAULT true,
	id serial NOT NULL
)
WITH (
	OIDS=FALSE
) ;
CREATE INDEX tusers__id_idx ON twitter.tusers USING btree (_id, id) ;
