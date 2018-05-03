#!/bin/bash
CC="sm_compile.sh"
PWD=$(pwd)

filepath=$(dirname "$1")
filename=$(basename "$1" .sc)
old="$filepath/.$filename.sb.src"
echo "Deleting $old"

rm -f $old
${CC} ${PWD}/$1
