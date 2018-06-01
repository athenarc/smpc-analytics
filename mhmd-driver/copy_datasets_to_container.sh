#!/bin/sh

CONTAINER_NAME="$1"

sudo docker cp ../datasets/patients.json $CONTAINER_NAME:/patients.json
