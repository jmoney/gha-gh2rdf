#!/bin/sh

if [[ $3 == "issues" ]];
then
    python3 /app/main.py --owner $1 --repo $2 --issues > $5
elif [[ $3 == "pull-requests" ]];
then
    python3 /app/main.py --owner $1 --pull-requests --org $4 > $5
else
    echo "Invalid argument"
    exit 1
fi