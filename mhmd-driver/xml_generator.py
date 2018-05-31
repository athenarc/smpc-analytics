#!/usr/bin/python
import pandas as pd
import os.path
import sys
import math
import argparse
from huepy import *

parser = argparse.ArgumentParser()
parser.add_argument('data', help= 'Path to csv file (_filtered_edited.csv)')
parser.add_argument('--float', help= 'Optional argument to force all columns have type float64', action='store_true')
parser.add_argument('--table', help= 'Optional table name')
args = parser.parse_args()

DATASET = args.data

if not os.path.exists(DATASET):
    print(bad('Unable to find dataset, please specify one.'))
    sys.exit(1)

print(run('Generating XML data from csv dataset: "' + DATASET + '"'))

DIRECTORY, BASENAME = os.path.split(DATASET)
BASENAME = os.path.splitext(BASENAME)[0]
OUTPUT = os.path.join(DIRECTORY, BASENAME + '.xml')

table_name = BASENAME
if args.table != None:
    table_name = args.table

def main():
    df=pd.read_csv(DATASET,sep=',')
    with open(OUTPUT,'w') as output:
        output.write('<table name="' + table_name + '" dataSource="DS1" handler="import-script.sb">\n')
        for attribute in df.columns:
            if args.float:
                infered_type = 'float64'
            else:
                infered_type = str(df[attribute].dtype)
            output.write('\t<column key="true" type="primitive">\n')
            output.write('\t\t<source name="' + attribute + '" type="' + infered_type + '"/>\n')
            output.write('\t\t<target name="' + attribute + '" type="' + infered_type + '"/>\n')
            output.write('\t</column>\n')
        output.write('</table>\n')
    print(good('Created file: "' + OUTPUT + '"'))

if __name__ == '__main__':
    main()
