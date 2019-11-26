#!/usr/bin/env bash

# follow readme:
# https://github.com/mangroveorg/datawinners
# https://github.com/mangroveorg/mangrove

function log {
  echo "***** $1"
  echo ""
}

function install_python_env {
    log "Install python env"
    sudo apt-get install python-virtualenv
    sudo apt install python-pip
    [ -d ~/virtual_env ] || mkdir virtual_env
	cd virtual_env
	virtualenv datawinners
	[ -f ~/.bash_profile ] || touch ~/.bash_profile
	echo 'alias dw="source /home/dw/mangroveorg/datawinners/virtual_env/datawinners/bin/activate"' >> ~/.bash_profile
	alias run_dw="dw && cd /home/dw/mangroveorg/datawinners && python datawinners/manage.py runserver 0.0.0.0:8044"
	echo 'export PATH=/usr/lib/postgresql/9.5/bin/:$PATH' >> ~/.bash_profile
	. ~/.bash_profile
}

function install_package {
    log "Install packages"
    sudo apt-get update
    sudo apt-get install python-psycopg2 python-setuptools

    # DB
    sudo apt-get install postgresql postgresql-contrib
    sudo apt-get install postgis
    sudo apt-get install couchdb
    sudo apt-get install gdal-bin
    sudo apt-get install libproj-dev
    sudo apt-get install libgdal-dev
    sudo apt-get install memcached
    export CPLUS_INCLUDE_PATH=/usr/include/gdal
    export C_INCLUDE_PATH=/usr/include/gdal
    export LC_ALL="en_US.UTF-8"
    export LC_CTYPE="en_US.UTF-8"
    ### pip install GDAL
    sudo apt-get install geoip-database
    sudo apt-get install gettext
    sudo apt-get install python-numpy
    ### Do not forget to install & configure elasticsearch as described here: https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-16-04
}

function init_db {
    log "Init DB"
    [ -d /usr/local/var/postgres9 ] || sudo mkdir -p /usr/local/var/postgres9
    chown postgres /usr/local/var/postgres9
    sudo -su postgres
    initdb /usr/local/var/postgres9
    pg_ctl -D /usr/local/var/postgres9 -l /usr/local/var/postgres9/server.log start
}

function create_datawinners_db {
    log "Create datawinners DB"
	createdb geodjango
	createlang plpgsql geodjango
	psql -d geodjango -c 'create role jenkins login createdb createrole;'
	psql -d geodjango -f '/usr/share/postgresql/9.5/contrib/postgis-2.2/postgis.sql'
	psql -d geodjango -f '/usr/share/postgresql/9.5/contrib/postgis-2.2/spatial_ref_sys.sql'
	psql -d geodjango -c 'grant all privileges on all tables in schema public to jenkins;'
}

function create_mangrove_db {
    log "Create mangrove DB"
	createdb mangrove
	createlang plpgsql mangrove
	psql -d mangrove -f '/usr/share/postgresql/9.5/contrib/postgis-2.2/postgis.sql'
	psql -d mangrove -f '/usr/share/postgresql/9.5/contrib/postgis-2.2/legacy_gist.sql'
	psql -d mangrove -f '/usr/share/postgresql/9.5/contrib/postgis-2.2/spatial_ref_sys.sql'
	psql -d mangrove -c 'grant all privileges on all tables in schema public to jenkins;'
}

function create_postgis_db {
    log "Create postgis DB"
	POSTGIS_SQL_PATH=/usr/share/postgresql/9.5/contrib/postgis-2.2
	createdb -E UTF8 template_postgis # Create the template spatial database.
	createlang -d template_postgis plpgsql # Adding PLPGSQL language support.
	psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
	psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql # Loading the PostGIS SQL routines
	psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
	psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;" # Enabling users to alter spatial tables.
	psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
	psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
}

function clone_code_base {
    log "Clone code base"
    [ -d /home/dw/mangroveorg] || mkdir /home/dw/mangroveorg
    cd /home/dw/mangroveorg
    git clone https://github.com/mangroveorg/datawinners.git datawinners
    #git clone https://github.com/mangroveorg/mangrove.git mangrove #cloned in virtual_env
    git clone https://github.com/mangroveorg/shape_files.git shape_files
}

function install_dependency {
    log "Install dependencies"
	dw
	cd /home/dw/mangroveorg/datawinners
	pip install -r ./requirements.pip
	pip install django_compressor
	python datawinners/manage.py syncdb
	python datawinners/manage.py migrate
	python datawinners/manage.py loadshapes

	couchdb -b
	./build.sh init
}

function main {
    install_python_env
	install_package
    init_db
	create_datawinners_db
	create_mangrove_db
	create_postgis_db
	clone_code_base
	install_dependency
	log 'environment is set!'
}

main