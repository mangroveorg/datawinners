First Install Steps:
=====================


Requirements
-------------------

* Python 2.7
* Python headers (sudo apt-get install python-dev)
* CouchDB (sudo apt-get install couchdb)
* PostgreSQL (sudo apt-get install postgres)
* Geometry Engine - Open Source (sudo apt-get install geos)
* PostGIS (sudo apt-get install postgis)
* Pip (easy_install pip)
* VirtualEnv (pip install virtualenv)
* [Optional] VirtualEnvWrapper (pip install virtualenvwrapper)
* NumPy (pip install numpy)
* Geospatial Data Abstraction Library (sudo apt-get install gdal)

1. Create a virtualenv
--------------------
virtualenv ve && source ve/bin/activate

    or with virtualenvwrapper

mkvirtualenv mangrove

2. Install required python packages
--------------------
pip install -r requirements.pip

3. Create local_settings.py
--------------------
cp src/datawinners/local_settings_example.py src/datawinners/local_settings.py

4. Create Postgres DB
--------------------
createdb geodjango
createlang plpgsql geodjango
psql -d geodjango -c 'create role jenkins login createdb createrole;'
psql -d geodjango -f '/usr/local/Cellar/postgis/1.5.3/share/postgis/postgis.sql'
psql -d geodjango -f '/usr/local/Cellar/postgis/1.5.3/share/postgis/spatial_ref_sys.sql'
psql -d geodjango -c 'grant all privileges on all tables in schema public to jenkins;'

5. Load Shape Files
--------------------
Clone https://github.com/mangroveorg/shape_files.git as a sibling to mangrove
python src/datawinners/manage.py syncdb
python src/datawinners/manage.py migrate
python src/datawinners/manage.py loadshapes

6. Make trans tag work
--------------------
brew install gettext
ln -s /usr/local/Cellar/gettext/0.18.1.1/bin/msgfmt .ve/bin/msgfmt(Notes, the virtual environment path)
cd src/datawinners/
python manage.py compilemessages

Test dependencies!
=====================

In order to properly run Django tests our database user will need
permissions to create a new database. Here's how to do it:

psql -d postgres -c 'ALTER ROLE jenkins WITH CREATEDB;'

Also, a template called template_postgis should be created. This might
be part of your PostGIS installation, but you can also create it
yourself by following the instructions at
http://geospatial.nomad-labs.com/2006/12/24/postgis-template-database/

To run functional tests you will either need a version of Firefox
supported by Selenium (this generally means not the latest version) or
you will need Google Chrome. For local development tests tend to run
more reliably with Chrome.

If you choose to do this you will also need to download chromedriver
from http://code.google.com/p/chromium/downloads/list

For best results put the chromedriver binary in your virtual
environment's bin folder. You may also put it in /usr/local/bin or
somewhere else in PATH. However, symlinking ve/bin/chromedriver =>
/usr/local/bin/chromedriver doesn't seem to work.

Run tests!
=====================

./runtests.sh ut
./runtests.sh ft

Push to GitHub
=====================
And hopefully Jenkins will run tests, and they will pass.
