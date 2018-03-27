#!/usr/bin/python
import pandas as pd
import numpy as np
import os.path
import sys
import math
import json
import csv

if len(sys.argv) > 1:
    DATASET = sys.argv[1]
else:
    DATASET = 'syndata_upload_and_scaling_tests/centricity_identified.csv'

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
OUTPUT = DIRECTORY + '/' + BASENAME + '_edited.csv'
SERIALIZED = DIRECTORY + '/' + BASENAME + '_mapped_values.json'

def main():
    print "Initializing ..."
    df=pd.read_csv(DATASET,sep=',')
    attribute_map = {}
    attribute_counter = {}
    rows = df.shape[0]
    string_attributes = []
    for attribute in df.columns:
        column = df[attribute]
        infered_type = str(column.dtype)
        if infered_type == 'object':
            attribute_map[attribute] = {}
            attribute_counter[attribute] = 0
            string_attributes.append(attribute)
    print "Done initializing"

    print "Writing to csv ..."
    with open(OUTPUT, 'w') as csv_edited:
        dataWriter = csv.writer(csv_edited, delimiter=',')
        dataWriter.writerow(df.columns.values)
        for i, row in df.iterrows():
            for attribute in string_attributes:
                mapped_values = attribute_map[attribute]
                value = row[attribute]
                if value in mapped_values:
                    row[attribute] = mapped_values[value]
                else:
                    ai = attribute_counter[attribute]
                    row[attribute] = ai
                    mapped_values[value] = ai
                    attribute_counter[attribute] += 1
            attribute_map[attribute] = mapped_values
            dataWriter.writerow(row)

    print "Serializing maps ..."
    with open(SERIALIZED, 'w') as data_file:
        j = json.dumps(attribute_map)
        data_file.write(j)

if __name__ == '__main__':
    main()
