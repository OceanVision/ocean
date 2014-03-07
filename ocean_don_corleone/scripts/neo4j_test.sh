#!/bin/bash
source ./init.sh
(( `ps ax | grep neo4j | wc -l` > 1 ))
