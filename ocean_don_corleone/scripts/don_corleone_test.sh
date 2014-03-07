#!/bin/bash
source ./init.sh
(( `ps ax | grep ocean_don_corleone | wc -l` > 1 ))
