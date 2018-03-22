#!/usr/bin/python
import pandas as pd
import numpy as np
import os.path
import sys
import math

if len(sys.argv) > 1:
    DATASET = sys.argv[1]
else:
    DATASET = 'syndata_upload_and_scaling_tests/centricity_identified.csv'

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
OUTPUT = DIRECTORY + '/' + BASENAME + '_edited.csv'

def main():
    df=pd.read_csv(DATASET,sep=',')
    for attribute in df.columns:
        infered_type = str(df[attribute].dtype)
        if infered_type == 'object':
            df[attribute] = 0
    df.to_csv(OUTPUT, sep=',', index=False)

if __name__ == '__main__':
    main()
