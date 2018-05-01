#!/usr/bin/python
import pandas as pd
import numpy as np
import os.path
import sys
import math
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--path', help= 'Path to csv file (_filtered_edited.csv)')
args = parser.parse_args()

if args.path is not None:
    DATASET = args.path
else:
    DATASET = '../datasets/analysis_test_data/cvi_identified.csv'

print('Generating XML data from csv dataset: "' + DATASET + '"\n')

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
OUTPUT = DIRECTORY + '/' + BASENAME + '.xml'

def main():
    df=pd.read_csv(DATASET,sep=',')
    with open(OUTPUT,'w') as output:
        output.write('<table name="' + BASENAME + '" dataSource="DS1" handler="import-script.sb">\n')
        for attribute in df.columns:
            infered_type = str(df[attribute].dtype)
            output.write('\t<column key="true" type="primitive">\n')
            output.write('\t\t<source name="' + attribute + '" type="' + infered_type + '"/>\n')
            output.write('\t\t<target name="' + attribute + '" type="' + infered_type + '"/>\n')
            output.write('\t</column>\n')
        output.write('</table>\n')
    print('\nCreated file: "' + OUTPUT + '"')

if __name__ == '__main__':
    main()
