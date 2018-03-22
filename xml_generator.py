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

if __name__ == '__main__':
    main()
