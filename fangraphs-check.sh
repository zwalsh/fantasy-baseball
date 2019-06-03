#!/bin/bash
export ENV=PROD
cd "$( dirname ${BASH_SOURCE[0]} )"
python3.6 check_fg_updated.py
