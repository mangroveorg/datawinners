#!/bin/bash
DWROOT_DIR=$(pwd)
MGROOT_DIR=$DWROOT_DIR/../mangrove
. go.sh

function update_source {
    echo "Update source code ...."
    git pull --rebase
    (cd $MGROOT_DIR && git pull --rebase)
}

function main {
	case $1 in
		init) init_env;;
		pc) pre_commit;;
		ut) unit_test;;
		ft) function_test;;
		couch) recreate_couch_db;;
		feed) recreate_feed_db;;
		rd) restore_postgresql_database;;
		us) update_source;;
		cm) compile_messages;;
		rsdb) restore_couchdb_and_postgres;;
		rs) run_server;;
		*) show_help && exit 1;;
	esac	
}

main $@
