from fabric.api import run
from fabric.context_managers import cd, settings

def deploy(build_number,home_dir,virtual_env):
    """build_number : hudson build number to be deployed
       home_dir: directory where you want to deploy the source code
       virtual_env : path to your virtual_env folder
    """
    run("export COMMIT_SHA=`curl http://hudson.mvpafrica.org:8080/job/Mangrove-develop/%s/artifact/last_successful_commit_sha`" % (build_number,))

    code_dir = home_dir+'/mangrove'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
           run("git clone git://github.com/mangroveorg/mangrove.git %s" % code_dir)
        with cd(code_dir):
            run("git checkout develop")
            run("git pull origin develop")
            if run("git branch -a|grep %s" % build_number).failed:
                run("git checkout -b %s $COMMIT_SHA" % (build_number,) )
            else:
                run("git branch -D %s" % build_number)
                run("git checkout -b %s $COMMIT_SHA" % (build_number,) )
            
            activate_and_run(virtual_env,"pip install -r requirements.pip")
        with cd(code_dir+'/src/datawinners'):
            activate_and_run(virtual_env,"python manage.py syncdb")

def activate_and_run(virtual_env,command):
    run('source %s/bin/activate && ' % virtual_env + command)