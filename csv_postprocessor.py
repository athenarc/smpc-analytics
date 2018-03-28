#!/usr/bin/python
from __future__ import print_function
import pandas as pd
import numpy as np
import os.path
import sys
import json


if len(sys.argv) > 1:
    ID3_RESULTS = sys.argv[1]
    INITIAL_DATASET = sys.argv[2]
else:
    ID3_RESULTS = 'syndata_upload_and_scaling_tests/id3.out'
    INITIAL_DATASET = 'syndata_upload_and_scaling_tests/centricity_identified_filtered_edited.csv'

# Directory and name of json file
DIRECTORY, INITIAL_BASENAME = os.path.split(INITIAL_DATASET)
INITIAL_BASENAME = os.path.splitext(INITIAL_BASENAME)[0]
SERIALIZED = DIRECTORY + '/' + INITIAL_BASENAME + '_mapped_values.json'

# Directory and name of id3 results file
DIRECTORY, ID3_BASENAME = os.path.split(ID3_RESULTS)
ID3_BASENAME = os.path.splitext(ID3_BASENAME)[0]
OUTPUT = DIRECTORY + '/' + ID3_BASENAME + '_postprocessed.out'


def main():
    print("Deserializing maps ...")
    map_file = open(SERIALIZED)
    attribute_map = json.load(map_file)

    print("Reconstructing initial data ...")
    df = pd.read_csv(INITIAL_DATASET, sep=',')
    data_file = open(ID3_RESULTS)

    prev_word = ""
    prev_attribute = ""
    for line in data_file:
        for word in line.split():
            if "[" in prev_word:
                prev_attribute = df.columns[int(word)]
                print(prev_attribute, end=' ')
            elif "==" == prev_word:
                mapped_values = attribute_map[prev_attribute]
                print(getValue(mapped_values, int(word))[0], end=' ')
            elif "-->" == prev_word and '[' not in word and '}' not in word and '{' not in word:
                mapped_values = attribute_map[df.columns[-1]]
                print(getValue(mapped_values, int(word))[0], end=' ')
            else:
                print(word, end=' ')
            prev_word = word

    print("\n\nClosing files ...")
    map_file.close()
    data_file.close()

def getValue(dict, value):
     return [key for key in dict.keys() if (dict[key] == value)]

if __name__ == '__main__':
    main()
