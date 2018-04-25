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
            COLUMNS = sys.argv[2]
        else:
            COLUMNS = 'datasets/analysis_test_data/columns.csv'
        if len(sys.argv) > 3:
            SUMMARY = sys.argv[3]
        else:
            SUMMARY = 'datasets/analysis_test_data/cvi_summary.csv'
    else:
        print('No arguement provided')
        sys.exit(1)

    main_counter = configuration[14:-5]

    configuration = json.load(open(configuration))
    numberOfFilters = 0
    if 'filters' in configuration:
        numberOfFilters = len(configuration['filters']['conditions'])
    df=pd.read_csv(COLUMNS,sep=',')
    numberOfHistograms = len(configuration['attributes'])
    histograms = [{} for x in range(numberOfHistograms)]
    for i in range(numberOfHistograms):
        histogram = histograms[i]
        histograms[i] = {}
        histograms[i]['attributes'] = [x['name'] for x in configuration['attributes'][i]]
        histograms[i]['attribute_indexes'] =  [df.columns.get_loc(attribute) for attribute in histograms[i]['attributes'] ]
        histograms[i]['cells'] = [x['cells'] for x in configuration['attributes'][i]]

    attributes_vmaps = ['{'+ ', '.join([str(x) for x in histograms[i]['attribute_indexes']]) +'}' for i in range(numberOfHistograms)]
    cells_vmaps = ['{'+ ', '.join([str(x) for x in histograms[i]['cells']]) +'}' for i in range(numberOfHistograms)]
    mins = []
    maxs = []
    summary = pd.read_csv(SUMMARY, sep = ',')
    for attribute in df.columns:
        if attribute in summary['Field'].values:
            mins.append(summary[summary['Field']==attribute][' Min'].item())
            maxs.append(summary[summary['Field']==attribute][' Max'].item())
        else:
            mins.append(0.0)
            maxs.append(0.0)
    main_f += '''
    pd_shared3p float64[[1]] imported_mins('''+ str(len(mins)) +''') =''' + '{'+ ', '.join([str(x) for x in mins]) +'}' + ''';
    pd_shared3p float64[[1]] imported_maxs('''+ str(len(maxs)) +''') =''' + '{'+ ', '.join([str(x) for x in maxs]) +'}' + ''';
    '''
    if numberOfFilters > 0:
        bool_op = quote(configuration['filters']['operator'])
        main_f += '''
    string bool_op = ''' + bool_op + ''';
        '''
        filter_attributes_indexes = [df.columns.get_loc(attribute) for attribute in [x['attribute'] for x in configuration['filters']['conditions']] ]
        constraint_attributes = '{'+ ', '.join([str(x) for x in filter_attributes_indexes]) +'}'
        main_f += '''
    uint64[[1]] constraint_attributes = '''+ constraint_attributes + ';'
        operators_enum = {'>' : 0, '<' : 1, '=': 2 }
        filter_operators_indexes = [operators_enum[x] for x in [x['operator'] for x in configuration['filters']['conditions']]]
        constraint_operators = '{'+ ', '.join([str(x) for x in filter_operators_indexes]) +'}'
        main_f += '''
    uint64[[1]] constraint_operators = '''+ constraint_operators + ';'
        constraint_values = '{'+ ', '.join([quote(x) for x in [x['value'] for x in configuration['filters']['conditions']]]) +'}'
        main_f += '''
    float64[[1]] constraint_values = '''+ constraint_values + ';'


    main_f += '''
    uint64 attributes_vmap = tdbVmapNew();
    uint64 cells_vmap = tdbVmapNew();
    uint64[[1]] vector_value;
'''
    for i in range(numberOfHistograms):
        main_f +='''
    vector_value = '''+ attributes_vmaps[i] + ''';
    tdbVmapAddValue(attributes_vmap, "''' + str(i) + '''", vector_value);
    vector_value = ''' + cells_vmaps[i] + ''';
    tdbVmapAddValue(cells_vmap, "''' + str(i) + '''", vector_value);
'''

    if 'datasources' in configuration:
        numberOfDatasets = len(configuration['datasources'])
        data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(configuration['datasources'][i]) + ";" for i in range(len(configuration['datasources']))])

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
    uint64 histograms = multiple_histograms(datasource, providers_vmap, data_providers_num, '''+str(numberOfHistograms)+'''::uint64, attributes_vmap, cells_vmap, imported_mins, imported_maxs, bool_op, constraint_attributes, constraint_operators, constraint_values);'''
    else:
        main_f += '''
    uint64 histograms = multiple_histograms(datasource, providers_vmap, data_providers_num, '''+str(numberOfHistograms)+'''::uint64, attributes_vmap, cells_vmap, imported_mins, imported_maxs);'''
    main_f += '''
    pd_shared3p uint64[[1]] res;
    uint64[[1]] cells_res;
    '''
    for i in range(numberOfHistograms):
        main_f +='''
    res = tdbVmapGetValue(histograms, "'''+ str(i) +'''", 0 :: uint64);
    cells_res = tdbVmapGetValue(cells_vmap, "'''+ str(i) +'''", 0 :: uint64);
    print(arrayToString(cells_res), " Histogram");
    printVector(declassify(res));
    print("\\n");
'''
    main_f += '}'

    with open('histogram_main_' + main_counter + '.sc', 'w') as output:
        output.write(imports)
        output.write(main_f)

if __name__ == '__main__':
    main()
