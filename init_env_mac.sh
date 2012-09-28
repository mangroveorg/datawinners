#!/usr/bin/env bash

function install_package {
	brew search postgis
	brew tap homebrew/versions
	sed -i .bak 's/postgresql/postgresql9/g' /usr/local/Library/Formula/postgis15.rb
	brew install postgis15
	brew install couchdb
	brew install gdal
	brew install geoip
	brew install gettext
	sudo brew link gettext
	pip install numpy
}

function install_python_env {
	curl -o setuptools-0.6c11-py2.7.egg http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg#md5=bfa92100bd772d5a213eedd356d64086
	sudo sh setuptools-0.6c11-py2.7.egg
	sudo easy_install pip 
	sudo pip install virtualenv
	[ -d ~/virtual_env ] || mkdir virtual_env 
	cd virtual_env
	virtualenv datawinners
	[ -f ~/.bash_profile ] || touch ~/.bash_profile 
	echo 'alias dw="source ~/virtual_env/datawinners/bin/activate"' >> ~/.bash_profile
	echo 'export PATH=/usr/local/Cellar/postgresql9/9.0.8/bin:$PATH' >> ~/.bash_profile
	. ~/.bash_profile
}


function init_db {
	initdb /usr/local/var/postgres9
	[ -d /usr/local/var/postgres9 ] || mkdir -p /usr/local/var/postgres9
	pg_ctl -D /usr/local/var/postgres9 -l /usr/local/var/postgres9/server.log start
}


function create_datawinners_db {
	createdb geodjango  
	createlang plpgsql geodjango  
	psql -d geodjango -c 'create role jenkins login createdb createrole;'  
	psql -d geodjango -f '/usr/local/share/postgis/postgis.sql'  
	psql -d geodjango -f '/usr/local/share/postgis/spatial_ref_sys.sql'  
	psql -d geodjango -c 'grant all privileges on all tables in schema public to jenkins;'
}


function create_postgis_db {
	POSTGIS_SQL_PATH=/usr/local/share/postgis  
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
  [ -d ~/workspace] || mkdir ~/workspace
  cd ~/workspace
  clone_repository datawinners
  clone_repository mangrove
  clone_repository shape_files
}

function clone_repository {
 git clone https://github.com/mangroveorg/$1.git $1
}

function install_dependency {
	dw
	cd ~/workspace/datawinners
	python datawinners/manage.py syncdb 
	python datawinners/manage.py migrate 
	python datawinners/manage.py loadshapes

	couchdb -b
	./build.sh init	
}

function main {
	install_package 
	install_python_env 
	init_db 
	create_datawinners_db 
	create_postgis_db
	clone_code_base
	install_dependency
}

main