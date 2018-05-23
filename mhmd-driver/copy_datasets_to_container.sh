#!/bin/sh

CONTAINER_NAME="$1"

sudo docker cp ../datasets/patient_files/ $CONTAINER_NAME:/patient_files
