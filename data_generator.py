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
                if not is_number(A[i,j]) or math.isnan(A[i,j]):
                    A[i,j] = 0.0
                array += str(A[i,j]) + ','
        array = array[:-1]
        array += '}'
        var = 'pd_shared3p float64[[2]] imported_array'
        command = 'reshape('+ array +', '+ str(N) +', '+ str(M) +');'
        output.write(var + ' = ' + command + '\n')
        mins = [str(min([A[i,j] for i in range(N)])) for j in range(M)]
        # mins = [min(A[:,j]) for j in range(M)]
        mins = '{' + ','.join(mins) + '}'
        maxs = [str(max([A[i,j] for i in range(N)])) for j in range(M)]
        maxs = '{' + ','.join(maxs) + '}'
        # maxs = [max(A[:,j]) for j in range(M)]
        output.write('pd_shared3p float64[[1]] imported_mins(' + str(M) + ') = ' + mins + ';\n')
        output.write('pd_shared3p float64[[1]] imported_maxs(' + str(M) + ') = ' + maxs + ';\n')
        # output.write('for (uint64 j = 0; j < ' + str(M) + '; j++ ) ;' + '\n')
        # output.write('mins3[j] = min(array[:,j]);' + '\n')
        # output.write('uint64 M = array_shape[1];' + '\n')
        # output.write('uint64 M = array_shape[1];' + '\n')

    # uint64[[1]] array_shape = shape(array); // array -> variable from data_input.sc
    # uint64 N = array_shape[0];
    # uint64 M = array_shape[1];
    # pd_shared3p float64[[1]] mins3(M);
    # pd_shared3p float64[[1]] maxs3(M);
    # for (uint64 j = 0; j < M; j++ ) {
    #   mins3[j] = min(array[:,j]);
    #   maxs3[j] = max(array[:,j]);
    # }



if __name__ == '__main__':
    main()
