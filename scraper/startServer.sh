#!/bin/sh

echo "username = $SCRAPYD_USERNAME" >> scrapyd.conf
echo "password = $SCRAPYD_PASSWORD" >> scrapyd.conf
scrapyd &> output.log &
scrapyd-deploy
tail -f output.log
