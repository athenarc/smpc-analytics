#!/bin/sh

CONTAINER_NAME="$1"

sudo docker cp ../datasets/patient.JSON $CONTAINER_NAME:/patients.json
