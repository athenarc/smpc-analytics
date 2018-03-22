#!/usr/bin/python
import pandas as pd
import numpy as np
import sys
import math

if len(sys.argv) > 1:
    DATASET = sys.argv[1]
else:
    DATASET = 'syndata_upload_and_scaling_tests/centricity_identified.csv'

OUTPUT = 'data_input.sc'
ROW_LIMIT = 1000

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def main():
    df=pd.read_csv(DATASET,sep=',')
    A = np.array(df)
    N = A.shape[0]
    N = min(N,ROW_LIMIT)
    M = A.shape[1]
    with open(OUTPUT,'w') as output:
        output.write('/* Rows: ' + str(N) + ' */' + '\n')
        output.write('/* Attributes (' + str(M) + ') */' + '\n')
        output.write('/**' + '\n')
        for i in range(len(df.columns)):
            col = df.columns[i]
            output.write(' * '+ col + ' (' + str(i) + ') : ' + str(df[col].dtype) + '\n')
        output.write('**/' + '\n')
        array = '{'
        for i in range(N):
            for j in range(M):
                value = A[i,j]
                if not is_number(value) or math.isnan(value):
                    value = 0.0
                array += str(value) + ','
        array = array[:-1]
        array += '}'
        var = 'pd_shared3p float64[[2]] array'
        command = 'reshape('+ array +', '+ str(N) +', '+ str(M) +');'
        output.write(var + ' = ' + command + '\n')

if __name__ == '__main__':
    main()
