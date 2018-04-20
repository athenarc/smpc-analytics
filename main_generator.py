import ast
import sys
import json
import pandas as pd

import os.path

indentation = '    '

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
'''

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def quote(x):
    if is_number(x):
        return str(x)
    else:
        return '"' + x + '"'

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
    numberOfFilters = 0
    if 'filter_attributes' in configuration:
        if isinstance(configuration['filter_attributes'], list):
            numberOfFilters = len(configuration['filter_attributes'])
        else:
            numberOfFilters = 1
    df=pd.read_csv(DATASET,sep=',')
    if isinstance(configuration['attributes'], list): # Multiple attributes
        attribute_indexes = [df.columns.get_loc(attribute) for attribute in configuration['attributes'] ]
    else: # Single attribute
        attribute_indexes = [df.columns.get_loc(configuration['attributes'])]
    attributes_vmap = '{'+ ', '.join([str(x) for x in attribute_indexes]) +'}'
    if numberOfFilters > 0:
        bool_op = quote(configuration['boolean_opreator'])
        main_f += '''
    string bool_op =''' + bool_op + ''';
        '''
        operators_enum = {'>' : 0, '<' : 1, '=': 2 }
        if isinstance(configuration['filter_attributes'], list):
            filter_attributes_indexes = [df.columns.get_loc(attribute) for attribute in configuration['filter_attributes'] ]
            # main_f += '{'+ ', '.join([str(x) for x in attribute_indexes]) +'}'
        else:
            filter_attributes_indexes = [df.columns.get_loc(configuration['filter_attributes'])]
        constraint_attributes = '{'+ ', '.join([str(x) for x in filter_attributes_indexes]) +'}'
        main_f += '''
    uint64[[1]] constraint_attributes = '''+ constraint_attributes + ';'
        if isinstance(configuration['filter_operators'], list):
            filter_operators_indexes = [operators_enum[x] for x in configuration['filter_operators']]
            # main_f += '{'+ ', '.join([str(x) for x in attribute_indexes]) +'}'
        else:
            filter_operators_indexes = [operators_enum[configuration['filter_operators']]]
        constraint_operators = '{'+ ', '.join([str(x) for x in filter_operators_indexes]) +'}'
        main_f += '''
    uint64[[1]] constraint_operators = '''+ constraint_operators + ';'
        if isinstance(configuration['filter_values'], list):
            constraint_values = '{'+ ', '.join([quote(x) for x in configuration['filter_values']]) +'}'
        else:
            constraint_values = '{'+ quote(configuration['filter_values']) +'}'
        main_f += '''
    float64[[1]] constraint_values = '''+ constraint_values + ';'

    main_f += '''
    uint64 attributes_vmap = tdbVmapNew();
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
    '''
    if 'datasources' in configuration:
        if isinstance(configuration['datasources'], list):
            numberOfDatasets = len(configuration['datasources'])
            data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(configuration['datasources'][i]) + ";" for i in range(len(configuration['datasources']))])
        else:
            numberOfDatasets = 1
            data_providers = indentation + "string table_0 = " + quote(configuration['datasources']) + ";"
        main_f += '''
    string datasource = "DS1";
    uint64 data_providers_num = ''' + str(numberOfDatasets) + ''';
'''
    main_f += data_providers
    main_f += '''
    // Create the data-providers list
    uint64 providers_vmap = tdbVmapNew();
'''
    for i in range(numberOfDatasets):
        main_f += '''
    tdbVmapAddString(providers_vmap, "0", table_'''+ str(i) +''');'''
    main_f += '''
    // Open connection to DB and Insert data to different tables
    print("Opening connection to db: ", datasource);
    tdbOpenConnection(datasource);
    print("Computing histograms");
'''
    if numberOfFilters > 0:
        main_f += '''
    uint64 histograms = multiple_histograms(datasource, providers_vmap, data_providers_num, '''+str(number_of_histograms)+'''::uint64, attributes_vmap, cells_vmap, imported_mins, imported_maxs, bool_op, constraint_attributes, constraint_operators, constraint_values);'''
    else:
        main_f += '''
    uint64 histograms = multiple_histograms(datasource, providers_vmap, data_providers_num, '''+str(number_of_histograms)+'''::uint64, attributes_vmap, cells_vmap, imported_mins, imported_maxs);'''
    main_f += '''
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
