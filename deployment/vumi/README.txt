To install

1. copy vumi from production
    a. copy the vumi code to the target machine: 'scp -r mangrover@178.79.145.58:/home/mangrover/vumi ~/workspace/vumi-prd'
    b. modify ~/workspace/vumi-prd/config/example_smpp.yaml as follows:

        # The unique name of this transport
        TRANSPORT_NAME: smpp_transport_1
        USER_ACCOUNT: vumi
        POST_TO_URL: http://localhost:8000/submission

        system_id: smppclient1  # username
        password: password      # password
        host: localhost         # the host to connect to
        port: 2775              # the port to connect to

        exchange_name: vumi.topic   # the AMQ exchange name
        exchange_type: topic        # the AMQ exchange type

2. set up vumi
    a.go to 'vumi-prd/docs/api.rst' and follow the instructions:

        To setup PostgreSQL:
            (datawinnsers)$ sudo -u postgres createuser --superuser --pwprompt vumi
            (datawinnsers)$ createdb -W -U vumi -h localhost -E UNICODE vumi

        For development start it within the virtual environment::
            (datawinnsers)$ python setup.py develop
            (datawinnsers)$ ./manage.py syncdb

    b.run 'python setup.py install' if necessary

3. install rabbitmq
    a. (datawinnsers)$ sudo apt-get install rabbitmq-server

To start vumi:

1. start rabbitmq
    a. (datawinnsers)$ sudo invoke-rc.d rabbitmq-server start

2. start vumi server
    a.(datawinnsers)$ python manage.py runserver 7000

3. start SMSC
    a. download smppsim package: 'SMPPSim.tar.gz' from 'http://www.seleniumsoftware.com/regform.php?itemdesc=SMPPSim.tar.gz'
    b. extract it
    c. modify %SMPPSIM_HOME%/config/smppsim.props:
        ESME_TO_ESME=TRUE
    d. $ sudo ./startsmppsim.sh
    e. visit 'http://localhost/inject_mo.htm' to subimt a message

4. start vumi consummers
    a. (datawinnsers)$ supervisord -c supervisord.example.conf
    b. to see logs:
        * go to '~/workspace/vumi-prd/logs'
        * 'tail -f smpp_transport_1.log'
        * 'tail -f smpp_worker_1.log'
    c. to see running status, visit 'http://localhost:9010/'


