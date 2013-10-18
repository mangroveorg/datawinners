#!/usr/bin/env bash


function log {
  echo "***** $1"
  echo ""
}

function create_mangrove_db {
 log "create mangrove db"
 createdb -E UTF8 mangrove -T template0
 createlang plpgsql mangrove
 psql -d mangrove -f '/usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql'
 psql -d mangrove -f '/usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql'
}

function create_postgis_template_db {
 log "create postgis template db..."
 createdb -E UTF8 template_postgis -T template0
 createlang -d template_postgis plpgsql
 psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
 psql -d template_postgis -f '/usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql' # Loading the PostGIS SQL routines
 psql -d template_postgis -f '/usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql'
 psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;" # Enabling users to alter spatial tables.
 psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
 psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
}

function create_db {
 log "create db..."
 create_mangrove_db && \
 create_postgis_template_db
}

function main {
  create_db && \
  log 'environment is ok!'
}

main
