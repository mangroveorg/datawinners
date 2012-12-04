#!/bin/bash

today=$(date -u +"%Y-%b-%d")
production_server=54.243.31.50
production_couch_path=/opt/couchbase-server/var/lib/
ssh_str=mangrover@$production_server
local_db_backup_dir=~/workspace/db_backup/prod_db/

mkdir -p $local_db_backup_dir

function backup_db(){
    echo "################${FUNCNAME[0]}($production_server)################"
     ssh $ssh_str -tt  '
        today=$(date -u +"%Y-%b-%d");
        couch_backup=~/mangrove_couchdb_backup_$today.tar
        echo $couch_backup
        echo "################backup couchdb...################"
        production_couch_path=/opt/couchbase-server/var/lib/
        cd $production_couch_path
        echo $production_couch_path
        tar -czvPf  $couch_backup  couchdb
        cd ~
        echo "################backup couchdb done.################"

        echo "################backup psql################"
        psql_backup=~/mangrove_postgres_dump_$today.gz
        pg_dump mangrove | gzip >  $psql_backup
        echo "################backup psql done################"

        exit'
     echo "################${FUNCNAME[0]} done.################"
 }

function copy_db(){
    echo "################${FUNCNAME[0]}################"
    scp $ssh_str:"~/mangrove_couchdb_backup_$today.tar ~/mangrove_postgres_dump_$today.gz" $local_db_backup_dir
    echo "################${FUNCNAME[0]} done.################"
}

function apply_couch(){
    echo -e "!!!Doesn't support yet. Please change the database dir of couchdb by yourself on configuration page of it."
    echo "################${FUNCNAME[0]}################"
    cd $local_db_backup_dir
    tar -xf mangrove_couchdb_backup_$today.tar
    echo "################${FUNCNAME[0]}################"
}

function apply_psql(){
    echo "################${FUNCNAME[0]}################"
    cd $local_db_backup_dir
    dropdb mangrove
    createdb -T template_postgis mangrove
    psql –d mangrove –c "create role mangrover login createdb createrole"
    psql –d mangrove –c "create role crs_reporting login creatdb createrole"
    gunzip mangrove_postgres_dump_$today
    psql mangrove < "mangrove_postgres_dump_$today"
    echo "################${FUNCNAME[0]} done ################"
}

function apply_prod_db(){
    echo "################${FUNCNAME[0]}################"
    apply_couch
    apply_psql
    echo "################${FUNCNAME[0]} done################"
}

function show_help(){
	echo "Usage: $0 [COMMAND]"
	echo "COMMAND"
	echo "backup: this will backup the psql and couchdb of production envirionment."
	echo "scp:    this will copy db backups to local envirionment."
	echo "apply:  this will apply db backups on local envirionment."
}

function main(){
	case $1 in
		backup) backup_db;;
		scp) copy_db;;
		apply) apply_prod_db;;
		all) backup_db && copy_db && apply;;
		*) show_help && exit 1;;
	esac
}
main $@
