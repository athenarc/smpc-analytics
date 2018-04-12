import ast
import sys
import json
import pandas as pd

import os.path

imports = '''
import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

import shared3p_table_database;
import table_database;
import data_input;

import histogram;
'''
main_f = '''void main(){
    uint64 attributes_vmap = tdbVmapNew();'''


def main():
    global main_f
    print('Generating main..')

    if len(sys.argv) > 1:
        configuration = sys.argv[1]
        if len(sys.argv) > 2:
            DATASET = sys.argv[2]
        else:
            DATASET = 'datasets/analysis_test_data/cvi_identified.csv'
    else:
        print('No arguement provided')
        sys.exit(1)
    
    main_counter = configuration[14:-5]
    
    number_of_histograms = 1
    configuration = json.load(open(configuration))
    df=pd.read_csv(DATASET,sep=',')
    if isinstance(configuration['attributes'], list): # Multiple attributes
        attribute_indexes = [df.columns.get_loc(attribute) for attribute in configuration['attributes'] ]
    else: # Single attribute
        attribute_indexes = [df.columns.get_loc(configuration['attributes'])]
    attributes_vmap = '{'+ ', '.join([str(x) for x in attribute_indexes]) +'}'
    main_f += '''
    uint64[[1]] vector_value;
    '''
    main_f +='''
    vector_value = '''+ attributes_vmap + ';'
    main_f += '''
    tdbVmapAddValue(attributes_vmap, "0", vector_value);
    uint64 cells_vmap = tdbVmapNew();
    '''
    cells = [str(x) for x in configuration['cells'] if x != '']
    cells_vmap = '{'+ ', '.join(cells) +'}'
    main_f += '''
    vector_value = ''' + cells_vmap + ';'
    main_f += '''
    tdbVmapAddValue(cells_vmap, "0", vector_value);
    print("Computing histograms");
    uint64 histograms = multiple_histograms(imported_array, '''+str(number_of_histograms)+'''::uint64, attributes_vmap, cells_vmap, imported_mins, imported_maxs);
    pd_shared3p uint64[[1]] res;
    '''
    for i in range(number_of_histograms):
        main_f +='''
    res = tdbVmapGetValue(histograms, "'''+ str(i) +'''", 0 :: uint64);
    uint64[[1]] cells_res = tdbVmapGetValue(cells_vmap, "'''+ str(i) +'''", 0 :: uint64);
    print(arrayToString(cells_res), " Histogram");
    printVector(declassify(res));
    print("\\n");
}
    '''
    with open('histogram_main_' + main_counter + '.sc', 'w') as output:
        output.write(imports)
        output.write(main_f)

if __name__ == '__main__':
    main()
