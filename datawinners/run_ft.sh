python manage.py recreatedb
cd ../func_tests
nosetests -v -a "functional_test"
