#!/bin/bash

set -e

SSH_CONFIG=$(dirname $0)/ssh-config

echo 'Checking if code is up to date...'
SOURCE_MD5="$(ssh -F $SSH_CONFIG solo -t "md5sum /tmp/solo-script.tar.gz | awk '{ print \$1 }'" | tr -d '\r\n')"
LOCAL_MD5="$(md5sum solo-script.tar.gz | awk '{ print $1 }' | tr -d '\r\n')"

if [ "$SOURCE_MD5" != "$LOCAL_MD5" ] || [ "$1" == "--force" ]; then
    echo 'Uploading new code...'
    scp -F $SSH_CONFIG solo-script.tar.gz solo:/tmp/solo-script.tar.gz
    ssh -F $SSH_CONFIG solo -t '
set -e
rm -rf /log/solo-script || true
mkdir /log/solo-script
cd /log/solo-script
tar -xvf /tmp/solo-script.tar.gz
virtualenv --clear env || virtualenv env
source ./env/bin/activate
pip install --no-index -UI ./wheelhouse/* 
'

else
    echo 'Code already up to date.'
fi
