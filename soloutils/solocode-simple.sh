#!/bin/bash

SSH_CONFIG=$(dirname $0)/ssh-config

rsync -avz -e "ssh -F $SSH_CONFIG" --exclude="*.pyc" --exclude="env" --exclude=".git" ./ solo:/etc/solo-script
