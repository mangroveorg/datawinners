#!/bin/bash

function prepare_mangrove_env {
	(cd $MGROOT_DIR && pip install -r requirements.pip && python setup.py develop)
}

function prepare_datawinner_log {
	sudo mkdir /var/log/datawinners
	sudo chmod 755 /var/log/datawinners
	sudo touch /var/log/datawinners/datawinners.log
	sudo touch /var/log/datawinners/datawinners-performance.log
	sudo touch /var/log/datawinners/datawinners_reminders.log
	sudo touch /var/log/datawinners/datawinners_xform.log
	sudo touch /var/log/datawinners/websubmission.log
	sudo touch /var/log/datawinners/sp-submission.log
	sudo chown $USER /var/log/datawinners/datawinners.log
	sudo chown $USER /var/log/datawinners/datawinners-performance.log
	sudo chown $USER /var/log/datawinners/datawinners_reminders.log
	sudo chown $USER /var/log/datawinners/datawinners_xform.log
	sudo chown $USER /var/log/datawinners/websubmission.log
	sudo chown $USER /var/log/datawinners/sp-submission.log
}

function patch_postgresql {
	cd $HOME/virtual_env/datawinner/lib/python2.7/site-packages/django
	patch -p1 < $DWROOT_DIR/postgis-adapter-2.patch
}

function prepare_datawinner_env {
        cp "$DWROOT_DIR/datawinners/config/local_settings_example.py" "$DWROOT_DIR/datawinners/local_settings.py"
 	pip install -r requirements.pip
}

function migrate_db {
	echo "go migrate database"
	python "$DWROOT_DIR/datawinners/manage.py" migrate
}

function pre_commit {
	echo "go pre commit"
        prepare_env && \
	unit_test && function_test
}

function prepare_env {
  	prepare_datawinner_log && update_source && prepare_mangrove_env && prepare_datawinner_env && patch_postgresql
}

function restore_couchdb_and_postgres {
  	restore_postgresql_database && \
	recreate_couch_db && \
	recreate_feed_db
}

function unit_test {
	echo "running unit test"
	compile_messages && \
	(cd "$DWROOT_DIR/datawinners" && python manage.py test --verbosity=2)
}

function recreate_couch_db {
	(cd "$DWROOT_DIR/datawinners" && python manage.py recreatedb)
}

function recreate_feed_db {
	(cd "$DWROOT_DIR/datawinners" && python manage.py recreatefeeddb)
}

function function_test {
	echo "running function test"
	cp "$DWROOT_DIR/datawinners/config/local_settings_example.py" "$DWROOT_DIR/func_tests/resources/local_settings.py"
	restore_postgresql_database && \
	recreate_couch_db && \
	compile_messages && \
	(cd "$DWROOT_DIR/func_tests" && nosetests --rednose -v -a functional_test)
}

function restore_postgresql_database {
	echo "recreating database"
	dropdb geodjango && createdb -T template_postgis geodjango && \
	(cd "$DWROOT_DIR/datawinners" && python manage.py syncdb --noinput && python manage.py migrate && python manage.py loadshapes)
}

function init_env {
	bash -c dw
	prepare_env && \
	(cd "$DWROOT_DIR/datawinners" &&  python manage.py compilemessages) && \
	restore_postgresql_database && \
	unit_test && function_test
}

function compile_messages {
    cd "$DWROOT_DIR/datawinners" && python manage.py compilemessages
}

function run_server {
    cd "$DWROOT_DIR/datawinners" && python manage.py runserver 0.0.0.0:8000
}

function show_help {
	echo "Usage: build.sh [COMMAND]"
	echo "COMMAND"
	echo "pc: \tthis will run all the unit test and function test"
	echo "ut: \tthis will run all the unit test"
	echo "ft: \tthis will run all the function test"
	echo "rd: \tdestory and recreate database"
	echo "us: \tupdate source codes of mangrove and datawinners"
	echo "cm: \tcimpile the django.po"
	echo "init: \t initialize environment for the first time"
	echo "rs: \t run server on the 127.0.0.1:8000"
}
