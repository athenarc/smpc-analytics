#!/usr/bin/python
import pandas as pd
import os.path
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('attributes', help = 'Attributes of the request. Semicolon (;) separated IDs.')
parser.add_argument('--path', help= 'Path to csv file')
parser.add_argument('--output', help = 'The output csv to be created.', default = '/cvi_filtered.csv')
args = parser.parse_args()

if args.path is not None:
    DATASET = args.path
else:
    DATASET = '/cvi_identified.csv'

print('Filtering csv dataset: "' + DATASET + '"\n')

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
# DESIRED_ATTRIBUTES = ['Gender', 'Height (cm)', 'Weight (kg)', 'Patient Age'] # order is important. Make sure label attribute is the last one.

DESIRED_ATTRIBUTES = args.attributes.split(';')

def main():
    df=pd.read_csv(DATASET,sep=',')
    filtered = df[DESIRED_ATTRIBUTES]
    cols = list(filtered)
    cols.insert(0, cols.pop())
    filtered.to_csv(args.output, sep=',', index=False)
    print('Filtered csv file: "' + args.output + '"\n')


if __name__ == '__main__':
    main()
