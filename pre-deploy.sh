#!/bin/bash

today=$(date -u +"%Y-%b-%d")
production_server=54.243.31.50
production_couch_path=/opt/apache-couchdb/var/lib/
ssh_str=mangrover@$production_server
local_db_backup_dir=~/workspace/db_backup/prod_db/$production_server

mkdir -p $local_db_backup_dir

function backup_db(){
    echo "################${FUNCNAME[0]} start################"
     ssh $ssh_str -tt  '
        today=$(date -u +"%Y-%b-%d");
        couch_main_backup=~/mangrove_couchdb_main_backup_$today
        couch_feed_backup=~/mangrove_couchdb_feed_backup_$today
        echo $couch_main_backup and $couch_feed_backup
        echo "################backup couchdb...################"
        production_couch_path=/opt/apache-couchdb/var/lib/
        cd $production_couch_path
        echo $production_couch_path
        tar -czvPf  $couch_main_backup.tar.gz  couchdb
        md5=`md5sum $couch_main_backup.tar.gz|cut -d " " -f 1`
        mv ${couch_main_backup}{,_${md5}}.tar.gz
        tar -czvPf  $couch_feed_backup.tar.gz  feed
        md5=`md5sum $couch_feed_backup.tar.gz|cut -d " " -f 1`
        mv ${couch_feed_backup}{,_${md5}}.tar.gz
        cd
        echo "################backup couchdb done.################"

        echo "################backup psql################"
        psql_backup=~/mangrove_postgres_dump_$today
        pg_dump mangrove | gzip >  $psql_backup.gz
        md5=`md5sum $psql_backup.gz|cut -d " " -f 1`
        mv ${psql_backup}{,_${md5}}.gz
        echo "################backup psql done################"

        exit'
     echo "################${FUNCNAME[0]} done.################"
 }

function copy_db(){
    echo "################${FUNCNAME[0]}################"
    scp $ssh_str:"~/mangrove_couchdb_main_backup_$today*.tar.gz ~/mangrove_couchdb_feed_backup_$today*.tar.gz ~/mangrove_postgres_dump_$today*.gz" $local_db_backup_dir
    cd $local_db_backup_dir
    couchdb_backup=`ls -t|grep mangrove_couchdb_main_backup_$today|sed -n 1p`
    couchdb_feed_backup=`ls -t|grep mangrove_couchdb_feed_backup_$today|sed -n 1p`
    psql_backup=`ls -t|grep mangrove_postgres_dump_$today|sed -n 1p`
    #Mac use md5 instead of md5sum
    md5_of_couchdb=`md5sum $couchdb_backup|awk '{print $NF}'`
    md5_of_couchdb_feed=`md5sum $couchdb_feed_backup|awk '{print $NF}'`
    md5_of_psql=`md5sum $psql_backup|awk '{print $NF}'`
    verify_md5 $couchdb_backup $md5_of_couchdb
    verify_md5 $couchdb_feed_backup $md5_of_couchdb_feed
    verify_md5 $psql_backup $md5_of_psql
    echo "################${FUNCNAME[0]} done.################"
}

function verify_md5(){
    if [[ $1 =~ $2 ]]
    then
        echo "MD5 verification SUCCESS for $1."
    else
        echo "MD5 verification FAILED for $1."
    fi
}

function apply_couch(){
    echo -e "!!!Doesn't support yet. Please change the database dir of couchdb by yourself on configuration page of it."
    echo "################${FUNCNAME[0]}################"
    cd $local_db_backup_dir
    couchdb_backup=`ls -t|grep mangrove_couchdb_main_backup_$today|sed -n 1p`
    tar -xvzf $couchdb_backup

    couchdb_feed_backup=`ls -t|grep mangrove_couchdb_feed_backup_$today|sed -n 1p`
    tar -xvzf $couchdb_feed_backup
    echo "################${FUNCNAME[0]}################"
}

function apply_psql(){
    echo "################${FUNCNAME[0]}################"
    cd $local_db_backup_dir
    psql_backup=`ls -t|grep mangrove_postgres_dump_$today|sed -n 1p`
    gunzip $psql_backup

    dropdb mangrove
    createdb -T template_postgis mangrove
    psql -d mangrove -c "create role mangrover login createdb createrole"
    psql -d mangrove -c "create role crs_reporting login createdb createrole"

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
