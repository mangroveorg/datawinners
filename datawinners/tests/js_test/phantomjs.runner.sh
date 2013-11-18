#!/bin/bash

function installPhantomjs(){
    echo "installing phantom"

    cd /usr/local/share
    sudo wget http://phantomjs.googlecode.com/files/phantomjs-1.9.1-linux-x86_64.tar.bz2
    sudo tar xjf phantomjs-1.9.1-linux-x86_64.tar.bz2
    sudo ln -s /usr/local/share/phantomjs-1.9.1-linux-x86_64/bin/phantomjs /usr/bin/phantomjs

    echo "Done installing phantom"
}

# sanity check to make sure phantomjs exists in the PATH
hash /usr/bin/env phantomjs &> /dev/null
if [ $? -eq 1 ]; then
    (installPhantomjs)
fi

# sanity check number of args
if [ $# -lt 1 ]
then
    echo "Usage: `basename $0` path_to_runner.html"
    echo
    exit 1
fi

SCRIPTDIR=$(dirname `perl -e 'use Cwd "abs_path";print abs_path(shift)' $0`)
TESTFILE=""
while (( "$#" )); do
        TESTFILE="$TESTFILE `perl -e 'use Cwd "abs_path";print abs_path(shift)' $1`"
    shift
done

# cleanup previous test runs
#cd $SCRIPTDIR
#rm -f *.xml

# fire up the phantomjs environment and run the test
cd $SCRIPTDIR
/usr/bin/env phantomjs ./js_libs/jasmine_reporters/phantomjs-testrunner.js $TESTFILE
