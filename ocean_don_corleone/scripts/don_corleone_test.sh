#!/bin/bash
source ./init.sh
(( `ps ax | grep ocean_don_corleone:app | wc -l` > 2 ))
