Installation steps
==================

Requirements
------------

* ubuntu 11.10
* python 2.7

0. Setting up your environment
------------------------------
1. Increase your apt-cache size:

sudo vi /etc/apt/apt.conf.d/70debconf

then add this line:

APT::Cache-Limit "100000000";

2. Make sure your user can sudo without password:

sudo visudo

Make sure you have this line:

%admin ALL=(ALL) NOPASSWD:ALL

Save the file, exit vi.

Make sure your user is in the "admin" group:

| (datawinner)user@host:~/workspace/datawinners$ groups
| vagrant adm dialout cdrom plugdev lpadmin sambashare admin

1. Clone datawinners from git
-----------------------------
| cd /tmp
| mkdir datawinners
| cd /tmp/datawinners
| git clone https://github.com/mangroveorg/datawinners.git

2. Install software, setup database and clone codebase from git
---------------------------------------------------------------
| cd /tmp/datawinners
| ./init_env_11.10.sh

If you successfully complete this step, you should see the following directories:

1. ~/virtual_env
2. ~/workspace

You no longer need /tmp/datawinners so let's get rid of that:

rm -rf /tmp/datawinners

You should also see the alias "dw" appended to your ~/.bashrc. Logout, log back in and type "dw". Your prompt should look like:

(datawinner)user@host:~$

3. Setup environments and run tests
-----------------------------------
| cd ~/workspace/datawinners
| ./build.sh init

This step sets up some log files, clones more git repos, installs dependencies and runs some tests.

By the end of this step your django server should be listening on port 8000.

If you hit ctrl-c to stop the server, some functional tests would run and fail. TODO: get rid of the functional tests and invoke them separately.

4. Access your server
---------------------
You can now point your browser to http://localhost:8000/

5. Run the server
-----------------
To start the server again in the future:

| cd ~/workspace/datawinners/datawinners
| python manage.py runserver 0.0.0.0:8000

Happy coding!
=============
