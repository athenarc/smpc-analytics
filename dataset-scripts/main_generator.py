import ast
import sys
import json
import argparse
import pandas as pd
from huepy import *

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
    print(run('Generating main..'))

    parser = argparse.ArgumentParser()
    parser.add_argument('configuration', help = 'Configuration file of the request')
    parser.add_argument('--columns', help = 'CSV File with the columns of the global schema.', default = 'datasets/analysis_test_data/columns.csv')
    parser.add_argument('--summary', help = 'CSV file with the summary of the dataset.', default = 'datasets/analysis_test_data/cvi_summary.csv')
    parser.add_argument('--DNS', help = 'File with the Hospitals names and IPS.', default = 'web/MHMDdns.json')
    args = parser.parse_args()

    uid = args.configuration.split('_')[-1].split('.')[0]

    configuration = json.load(open(args.configuration))
    numberOfFilters = 0
    if 'filters' in configuration:
        numberOfFilters = len(configuration['filters']['conditions'])
    df=pd.read_csv(args.columns,sep=',')

    total_attribute_number = 0
    total_attributes = []

    numberOfHistograms = len(configuration['attributes'])
    histograms = [{} for x in range(numberOfHistograms)]
    for i in range(numberOfHistograms):
        histogram = histograms[i]
        histograms[i] = {}
        histograms[i]['attributes'] = [x['name'] for x in configuration['attributes'][i]]
        histograms[i]['attribute_indexes'] =  list(range(total_attribute_number, total_attribute_number + len(histograms[i]['attributes'])))
        histograms[i]['cells'] = [x['cells'] for x in configuration['attributes'][i]]
        total_attribute_number += len(histograms[i]['attributes'])
        total_attributes += histograms[i]['attributes']

    attributes_vmaps = ['{'+ ', '.join([str(x) for x in histograms[i]['attribute_indexes']]) +'}' for i in range(numberOfHistograms)]
    cells_vmaps = ['{'+ ', '.join([str(x) for x in histograms[i]['cells']]) +'}' for i in range(numberOfHistograms)]
    mins = []
    maxs = []
    summary = pd.read_csv(args.summary, sep = ',')
    for attribute in total_attributes:
        if attribute in summary['Field'].values:
            mins.append(summary[summary['Field']==attribute][' Min'].item())
            maxs.append(summary[summary['Field']==attribute][' Max'].item())
        else:
            mins.append(0.0)
            maxs.append(0.0)
    print(mins, maxs)
    main_f += '''
    pd_shared3p float64[[1]] imported_mins('''+ str(len(mins)) +''') =''' + '{'+ ', '.join([str(x) for x in mins]) +'}' + ''';
    pd_shared3p float64[[1]] imported_maxs('''+ str(len(maxs)) +''') =''' + '{'+ ', '.join([str(x) for x in maxs]) +'}' + ''';
    '''
    if numberOfFilters > 0:
        bool_op = quote(configuration['filters']['operator'])
        main_f += '''
    string bool_op = ''' + bool_op + ''';
        '''
        filter_attributes_indexes = list(range(total_attribute_number, total_attribute_number + len(configuration['filters']['conditions'])))
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
        data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(configuration['datasources'][i] + '_' + uid ) + ";" for i in range(len(configuration['datasources']))])
    else:
        dns = json.load(open(args.DNS))
        available_datasources = dns.keys()
        numberOfDatasets = len(available_datasources)
        data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(available_datasources[i] + '_' + uid ) + ";" for i in range(len(available_datasources))])

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

    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        // Check if a table exists
        if (tdbTableExists(datasource, table)) {
          // Delete existing table
          print("Deleting table: ", table);
          tdbTableDelete(datasource, table);
        }
    }
'''
    main_f += '}'

    if os.path.isdir("./histogram/"):
        OUTPUT_DIR = './histogram/'
    elif os.path.isdir("../histogram/"):
        OUTPUT_DIR = '../histogram/'
    else:
        OUTPUT_DIR = './'
    with open(OUTPUT_DIR + 'main_' + uid + '.sc', 'w') as output:
        output.write(imports)
        output.write(main_f)
    print(good('Main generated at ' + OUTPUT_DIR + 'main_' + uid + '.sc'))

if __name__ == '__main__':
    main()
