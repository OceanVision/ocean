#!/bin/bash
SET=1

if [ "$1" = "-h" -o "$1" = "--help" ]
then
    echo "Usage: sh test.sh [-s <set>, --set=<set>]"
    return
fi

last_param=""
for param in "$@"
do
    if [ "$last_param" = "-s" ]
    then
        SET=$param
    elif [ "$param"==^--set\=.+$ ]
    then
        SET=$(echo $param | cut -c 7-)
    fi

    last_param=$param
done

sbt << EOF
test-only com.lionfish.correctness.Set$SET
EOF
