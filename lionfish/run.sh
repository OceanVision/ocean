#!/bin/bash
PORT=21
DEBUG=0

if [ "$1" = "-h" -o "$1" = "--help" ]
then
    echo "Usage: sh run.sh [-p <port>, --port=<port>] [--debug]"
    return
fi

last_param=""
for param in "$@"
do
    if [ "$param" = "--debug" ]
    then
        DEBUG=1
    elif [ "$last_param" = "-p" ]
    then
        PORT=$param
    elif [ "$param"=~^--port\=.+$ ]
    then
        PORT=$(echo $param | cut -c 8-)
    fi

    last_param=$param
done

final_params="run --port=$PORT"

if [ $DEBUG -eq 1 ]
then
    final_params="run --debug"
fi

sbt << EOF
$final_params
EOF
