#!/bin/sh
#set -x
function prepare_mangrove_env {
	cd ../mangrove && \
	pip install -r requirements.pip && \
	python setup.py develop && \
	cd ../datawinners
}

function prepare_datawinner_env {
	pip install -r requirements.pip && \
	cp datawinners/local_settings_example.py datawinners/local_settings.py
}

function migrate_db {
	python datawinners/manage.py migrate
}

function pre_commit {
	prepare_mangrove_env && \
	prepare_datawinner_env && \
	migrate_db && \
	unit_test && \
	function_test
}

function unit_test {
	echo "running unit test" && \
	cd datawinners && \
	python manage.py recreatedb && \
	python manage.py test &&\
	cd ..
}

function function_test {
	echo "running function test" && \
	cp datawinners/local_settings_example.py func_tests/resources/local_settings.py && \
	cd datawinners
	python manage.py migrate && \
	python manage.py recreatedb && \
	cd ../func_tests && \
	nosetests
}

function restore_database {
	echo "recreating database" && \
	dropdb geodjango && \
	createdb geodjango && \
    psql -d geodjango -f '/usr/local/share/postgis/postgis.sql' && \
	psql -d geodjango -f '/usr/local/share/postgis/spatial_ref_sys.sql' && \
	cd datawinners && \
	python manage.py syncdb && \
	python manage.py migrate && \
	python manage.py loadshapes
}

function show_help {
	echo "Usage: build.sh [COMMAND]"
	echo "COMMAND"
	echo "pc: \tthis will run all the unit test and function test"
	echo "ut: \tthis will run all the unit test"
	echo "ft: \tthis will run all the function test"
	echo "rd: \tdestory and recreate database"
}

function main {
	case $1 in
		pc) pre_commit;;
		ut) unit_test;;
		ft) function_test;;
		rd) restore_database;;
		*) show_help && exit 1;;
	esac
}

main $@
