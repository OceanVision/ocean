#!/bin/bash
(( `ps ax | grep don_corleone_server:app | wc -l` > 2 ))
