#!/usr/bin/python
import pandas as pd
import os.path
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--path', help= 'Path to csv file')
args = parser.parse_args()

if args.path is not None:
    DATASET = args.path
else:
    DATASET = '../datasets/analysis_test_data/cvi_identified.csv'

print('Filtering csv dataset: "' + DATASET + '"\n')

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
OUTPUT = DIRECTORY + '/' + BASENAME + '_filtered.csv'
DESIRED_ATTRIBUTES = ['Gender', 'Height (cm)', 'Weight (kg)', 'Patient Age'] # order is important. Make sure label attribute is the last one.


def main():
    df=pd.read_csv(DATASET,sep=',')
    filtered = df[DESIRED_ATTRIBUTES]
    cols = list(filtered)
    cols.insert(0, cols.pop())
    filtered.to_csv(OUTPUT,sep=',',index=False)
    print('Filtered csv file: "' + OUTPUT + '"\n')


if __name__ == '__main__':
    main()
