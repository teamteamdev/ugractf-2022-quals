#!/bin/bash

set -e

psql -v ON_ERROR_STP=1 --username="$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE USER synapse2 WITH PASSWORD 'synapse';
  CREATE DATABASE synapse2 TEMPLATE=template0 LC_COLLATE="C" LC_CTYPE="C" ENCODING=utf8;
  GRANT ALL PRIVILEGES ON DATABASE synapse2 TO synapse2;
EOSQL
