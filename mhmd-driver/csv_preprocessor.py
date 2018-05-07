#!/usr/bin/python
import pandas as pd
import numpy as np
import os.path
import sys
import math
import json
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--path', help= 'Path to csv filtered file (_filtered.csv)')
parser.add_argument('--id3', help= 'for id3', nargs='?', default=False)
args = parser.parse_args()

if args.path is not None:
    DATASET = args.path
else:
    DATASET = '../datasets/analysis_test_data/cvi_identified_filtered.csv'

print('Pre-processing csv dataset: "' + DATASET + '"')
if args.id3 != False:
    print('With ID3 argument\n')
else:
    print('Without ID3 argument\n')

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
OUTPUT = DIRECTORY + '/' + BASENAME + '_edited.csv'
SERIALIZED = DIRECTORY + '/' + BASENAME + '_edited_mapped_values.json'
CELLS = 4


def main():
    print "Initializing ..."
    df=pd.read_csv(DATASET,sep=',')
    attribute_map = {}
    attribute_min = {}
    attribute_max = {}
    attribute_counter = {}
    rows = df.shape[0]
    string_attributes = []
    for attribute in df.columns:
        attribute_map[attribute] = {}
        attribute_counter[attribute] = 0
        attribute_min[attribute] = min(df[attribute])
        attribute_max[attribute] = max(df[attribute])

    print "Done initializing"

    print "Writing to csv ..."
    with open(OUTPUT, 'w') as csv_edited:
        dataWriter = csv.writer(csv_edited, delimiter=',')
        dataWriter.writerow(df.columns.values)
        for i, row in df.iterrows():
            for attribute in df.columns:
                mapped_values = attribute_map[attribute]
                value = row[attribute]
                if str(value) == 'nan': # Missing value
                    row[attribute] = 0
                elif value in mapped_values:
                    row[attribute] = mapped_values[value]
                else:
                    if str(df[attribute].dtype) == 'object':
                        new_value = attribute_counter[attribute]
                        attribute_counter[attribute] += 1
                        mapped_values[value] = new_value
                    else:
                        if args.id3 != False:
                            minimum =  attribute_min[attribute]
                            width = (attribute_max[attribute] - minimum) / CELLS
                            new_value = int((value - minimum) / width)
                            if new_value == CELLS:
                                new_value -= 1
                            start = minimum + new_value*width
                            mapped_values['[' + str(start) + ', ' + str(start+width) + ')'] = new_value
                        else:
                            new_value = value
                    row[attribute] = new_value

            attribute_map[attribute] = mapped_values
            dataWriter.writerow(row)

    print "Serializing maps ..."
    with open(SERIALIZED, 'w') as data_file:
        j = json.dumps(attribute_map)
        data_file.write(j)
    print('\nEdited csv file: "' + OUTPUT + '"')
    print('Serialized maps file: "' + SERIALIZED + '"\n')

if __name__ == '__main__':
    main()
