for database in $(cat $1.txt)
do
    python ../datawinners/manage.py recreate_search_indexes $database
    echo $(date)": "$database >> ./completed.txt
done