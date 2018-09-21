import sys
import json
from huepy import *
import os.path
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--values', help = 'JSON file with the possible values of the categorical attributes of the dataset.', default = 'datasets/analysis_test_data/cvi_possible_values.json')
    parser.add_argument('--cvi_mapping', help = 'Output file with the cvi categorical attributes mapping (values to integers).', default = 'datasets/analysis_test_data/cvi_mapping.json')
    args = parser.parse_args()

    possible_values = json.load(open(args.values))

    mapping = {attribute : {value : counter for counter, value in enumerate(values)} for attribute, values in possible_values.items()}

    json.dump(mapping, open(args.cvi_mapping, 'w'))

if __name__ == '__main__':
    main()
