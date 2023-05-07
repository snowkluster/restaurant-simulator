#!/usr/bin/env bash
set -e

read -rp  "do you want to push or pull: " confirm

if [ "$confirm" == push ]
then
    git add .
    read -rp "Enter commit message: " Message
    git commit -m "$Message"
    git push -u origin master
elif [ "$confirm" == pull ]
then
    git pull
else
    echo "cannot find specified command"
fi