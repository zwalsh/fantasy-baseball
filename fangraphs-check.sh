#!/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
export ENV=PROD
cd "$( dirname ${BASH_SOURCE[0]} )"
python3.6 check_fg_updated.py
