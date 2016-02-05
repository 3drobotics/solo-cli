#!/bin/bash

set -e

PREVDIR=$(pwd)

rm -rf /tmp/solo-script || true
cp -rf . /tmp/solo-script

cd /tmp/solo-script
rm -rf env
virtualenv env
source ./env/bin/activate
echo 'import sys; import distutils.core; s = distutils.core.setup; distutils.core.setup = (lambda s: (lambda **kwargs: (kwargs.__setitem__("ext_modules", []), s(**kwargs))))(s)' > env/lib/python2.7/site-packages/distutils.pth
pip install wheel
set +e
pip wheel -r ./requirements.txt --build-option="--plat-name=py27" -w ./wheelhouse
set -e
tar -cvzf "$PREVDIR/solo-script.tar.gz" --exclude solo-script.tar.gz --exclude .git --exclude env -C /tmp/solo-script .
