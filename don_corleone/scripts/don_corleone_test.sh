#!/bin/bash
source ./init.sh
(( `ps ax | grep don_corleone:app | wc -l` > 2 ))
