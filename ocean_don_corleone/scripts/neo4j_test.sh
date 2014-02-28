#!/bin/bash
./init.sh
(( `ps ax | grep neo4j | wc -l` > 1 ))
