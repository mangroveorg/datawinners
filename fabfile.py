from fabric.api import run
from fabric.context_managers import cd, settings

def deploy(branch,commit_sha):
    code_dir = '/home/mangrover/mangrove'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
           run("git clone git://github.com/mangroveorg/mangrove.git %s" % code_dir)
    with cd(code_dir):
        run("git pull origin develop")
        run("git checkout -b %s %s" % (branch,commit_sha) )
        run("source %s/awe_ve/bin/activate" % code_dir )
        run("pip install -r requirements.pip")
    with cd(code_dir+'/src/datawinners'):
        run("python manage.py syncdb")
