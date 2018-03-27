#!/usr/bin/python
import pandas as pd
import os.path
import sys

if len(sys.argv) > 1:
    DATASET = sys.argv[1]
else:
    DATASET = 'syndata_upload_and_scaling_tests/centricity_identified.csv'

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
OUTPUT = DIRECTORY + '/' + BASENAME + '_filtered.csv'
DESIRED_ATTRIBUTES = ['Sex', 'Height', 'Weight', 'Age'] # order is important. Make sure label attribute is the last one.


def main():
    df=pd.read_csv(DATASET,sep=',')
    filtered = df[DESIRED_ATTRIBUTES]
    cols = list(filtered)
    cols.insert(0, cols.pop())
    filtered.to_csv(OUTPUT,sep=',',index=False)


if __name__ == '__main__':
    main()
