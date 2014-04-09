Copyright and license
---------------------

Copyright 2014 HNI

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Installation steps
==================

Requirements
------------

* ubuntu 12.04
* python 2.7
* java
* elasticsearch
* couchdb
* prostgres

0. Setting up your environment
------------------------------
1. Download and install sun java
    sudo apt-get install -y alien
    sudo apt-get update && \
    sudo apt-get install -y git curl alien && \
    alien -i --scripts <path_to_jdk.rpm downloaded from oracle something like ./jdk-7u25-linux-x64.rpm>

2. Install puppet
-----------------------------
| sudo apt-get install puppet
| wget -q https://gist.github.com/dileepbapat/6290962/raw/c3596fb5ce050afd7df3323ccf5ddb7f464bdb94/install_datawinners.sh
| bash ./install_datawinners.sh <env=dwdev|dwqa|dwprod>
|
4. Access your server
---------------------
If you installed env=dwdev you could access server by pointing your browser to https://localhost/

5. Run the server
-----------------
   By default uwsgi and nginx serves datawinners application it will be started at machine startup. Optionally you could start/stop
   using service command
   sudo service nginx stop
   sudo service uwsgi stop

   sudo service nginx start
   sudo service uwsgi start

