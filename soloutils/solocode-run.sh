#!/bin/bash

SSH_CONFIG=$(dirname $0)/ssh-config

# Ensure we have pip
solo install-pip

# In case files arent synced
$(dirname $0)/solocode-push.sh

echo ''

ssh -F $SSH_CONFIG solo -t "
set -e
cd /log/solo-script
source ./env/bin/activate
exec python $1
"
