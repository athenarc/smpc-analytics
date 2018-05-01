#!/usr/bin/python
from __future__ import print_function
import pandas as pd
import numpy as np
import os.path
import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--id3out', help= 'Path to ID3 output')
parser.add_argument('--path', help= 'Path to csv file (filtered & edited)')
args = parser.parse_args()

if args.path is not None:
    INITIAL_DATASET = args.path
else:
    INITIAL_DATASET = '../datasets/analysis_test_data/cvi_identified_filtered_edited.csv'

if args.id3out is not None:
    ID3_RESULTS = args.id3out
else:
    ID3_RESULTS = '../ID3/id3.out'

print('Post-processing csv dataset: "' + INITIAL_DATASET + '", with "' + ID3_RESULTS + '" output\n')


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
    tabs = 0
    for line in data_file:
        for word in line.split():
            if "{" == word :
                tabs +=1
                print('{')
            elif "}" == word :
                tabs -=1
                print("\t"*tabs, end='')
                print('}')
            elif "[" in prev_word:
                prev_attribute = df.columns[int(word)]
                print(prev_attribute, end=' ')
            elif "==" == prev_word:
                mapped_values = attribute_map[prev_attribute]
                print(getValue(mapped_values, int(word))[0], end=' ')
            elif "-->" == prev_word and '[' not in word and '}' not in word and '{' not in word:
                mapped_values = attribute_map[df.columns[-1]]
                print(getValue(mapped_values, int(word))[0], end='\n')
            elif "[" == word :
                print("\t"*tabs, end='')
                print("[", end=' ')
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
