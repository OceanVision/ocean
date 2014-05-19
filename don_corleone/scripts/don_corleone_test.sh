#!/bin/bash
source ./init.sh
(( `ps ax | grep don_corleone_server:app | wc -l` > 2 ))
