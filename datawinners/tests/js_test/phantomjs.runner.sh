#!/bin/bash

function installPhantomjs(){
    echo "installing phantom"
    mkdir -p ~/phantom
    mkdir -p ~/bin
    cd ~/phantom
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.7-linux-x86_64.tar.bz2
    tar xjf phantomjs-1.9.7-linux-x86_64.tar.bz2
    ln -s ~/phantom/phantomjs-1.9.7-linux-x86_64/bin/phantomjs ~/bin/phantomjs

    echo "Done installing phantom"
}

# sanity check to make sure phantomjs exists in the PATH
which ~/bin/phantomjs &> /dev/null
if [ $? -ne 0 ]; then
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
~/bin/phantomjs ./js_libs/jasmine_reporters/phantomjs-testrunner.js $TESTFILE
if [ $? -eq 0 ]
then
    echo -e "\e[0;32;47mAll DW JS test passed\e[0m"
    exit 0
else
    echo -e "\e[0;31;47mSome or all DW JS tests failed. Please check the logs above\e[0m"
    exit 1
fi