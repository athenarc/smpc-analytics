#!/bin/sh

CONTAINER_NAME="$1"

sudo docker cp ../datasets/patients.json $CONTAINER_NAME:/patients.json
sudo docker cp ../datasets/analysis_test_data/cvi_identified.csv $CONTAINER_NAME:/cvi_identified.csv
