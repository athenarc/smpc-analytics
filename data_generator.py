#!/usr/bin/python
import pandas as pd
import numpy as np
import sys
import math

if len(sys.argv) > 1:
    DATASET = sys.argv[1]
else:
    DATASET = 'datasets/analysis_test_data/cvi_identified_edited.csv'

OUTPUT = 'data_input.sc'
ROW_LIMIT = 1000

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
                array += str(A[i,j]) + ','
        array = array[:-1]
        array += '}'
        var = 'pd_shared3p ' + str(df[col].dtype) + '[[2]] imported_array'
        command = 'reshape('+ array +', '+ str(N) +', '+ str(M) +');'
        output.write(var + ' = ' + command + '\n')
        mins = [str(min([A[i,j] for i in range(N)])) for j in range(M)]
        mins = '{' + ','.join(mins) + '}'
        maxs = [str(max([A[i,j] for i in range(N)])) for j in range(M)]
        maxs = '{' + ','.join(maxs) + '}'
        output.write('pd_shared3p ' + str(df[col].dtype) + '[[1]] imported_mins(' + str(M) + ') = ' + mins + ';\n')
        output.write('pd_shared3p ' + str(df[col].dtype) + '[[1]] imported_maxs(' + str(M) + ') = ' + maxs + ';\n')


if __name__ == '__main__':
    main()
