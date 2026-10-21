



DROP DATABASE IF EXISTS tokomaju_dw;
DROP DATABASE IF EXISTS tokomaju_oltp;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'etl') THEN
    CREATE ROLE etl LOGIN PASSWORD 'etl_tokomaju';
  ELSE
    ALTER ROLE etl LOGIN PASSWORD 'etl_tokomaju';
  END IF;
END
$$;

CREATE DATABASE tokomaju_oltp OWNER etl;
CREATE DATABASE tokomaju_dw OWNER etl;

GRANT ALL PRIVILEGES ON DATABASE tokomaju_oltp TO etl;
GRANT ALL PRIVILEGES ON DATABASE tokomaju_dw TO etl;
