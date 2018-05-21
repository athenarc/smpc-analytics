#!/bin/sh

CONTAINER_NAME="$1"

sudo docker cp ../datasets/patient_files/ $CONTAINER_NAME:/patient_files
sudo docker cp ../datasets/mesh_mapping.json $CONTAINER_NAME:/mesh_mapping.json
sudo docker cp ../datasets/mtrees2018.csv $CONTAINER_NAME:/mtrees2018.csv
sudo docker cp ../datasets/mtrees2018_inverted.csv $CONTAINER_NAME:/mtrees2018_inverted.csv
