#!/bin/bash
source ./init.sh
(( `ps ax | grep don_corleone | wc -l` > 1 ))
