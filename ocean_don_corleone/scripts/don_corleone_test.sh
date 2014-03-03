#!/bin/bash
source ./init.sh
(( `ps ax | grep ocean_don_corleone.py | wc -l` > 1 ))
