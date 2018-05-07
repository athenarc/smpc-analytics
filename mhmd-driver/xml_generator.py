#!/usr/bin/python
import pandas as pd
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
    if os.path.exists('./datasets/analysis_test_data/cvi_identified.csv'):
        DATASET = './datasets/analysis_test_data/cvi_identified.csv'
    elif os.path.exists('../datasets/analysis_test_data/cvi_identified.csv'):
        DATASET = '../datasets/analysis_test_data/cvi_identified.csv'
    elif os.path.exists('../../datasets/analysis_test_data/cvi_identified.csv'):
        DATASET = '../../datasets/analysis_test_data/cvi_identified.csv'

if not os.path.exists(DATASET):
    print('\nUnable to find default dataset, please specify one.\n')
    sys.exit(-1)

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
            # if infered_type == 'object':
                # continue
            infered_type = 'float64'
            output.write('\t<column key="true" type="primitive">\n')
            output.write('\t\t<source name="' + attribute + '" type="' + infered_type + '"/>\n')
            output.write('\t\t<target name="' + attribute + '" type="' + infered_type + '"/>\n')
            output.write('\t</column>\n')
        output.write('</table>\n')
    print('Created file: "' + OUTPUT + '"')

if __name__ == '__main__':
    main()
