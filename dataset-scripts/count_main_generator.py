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

available_datasources = ['HospitalA', 'HospitalB', 'HospitalC']

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

    parser = argparse.ArgumentParser()
    parser.add_argument('configuration', help = 'Configuration file of the request')
    parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = 'mhmd-driver/mesh_mapping.json')
    args = parser.parse_args()


    print(run('Generating main..'))

    main_counter = args.configuration.split('_')[-1].split('.')[0]

    configuration = json.load(open(args.configuration))
    mapping = json.load(open(args.mapping))


    if 'datasources' in configuration:
        numberOfDatasets = len(configuration['datasources'])
        data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(configuration['datasources'][i]) + ";" for i in range(len(configuration['datasources']))])
    else:
        numberOfDatasets = len(available_datasources)
        data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(available_datasources[i]) + ";" for i in range(len(available_datasources))])

    attributes = configuration['attributes']
    attribute_values = [len(mapping[attribute]) for attribute in attributes]
    main_f += '''
    uint64 attributes_vmap = tdbVmapNew();
    uint64[[1]] Ps = {'''+ str(', '.join(map(str,attribute_values))) +'''};
    string datasource = "DS1";
    uint64 data_providers_num = ''' + str(numberOfDatasets) + ''';
'''
    for attribute in attributes:
        main_f += '''
    tdbVmapAddString(attributes_vmap, "0", ''' + quote(attribute) + ''');
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
    print("Computing histogram");
'''
    main_f += '''
    pd_shared3p uint64[[1]] histogram = histogram_categorical(datasource, providers_vmap, data_providers_num, attributes_vmap, Ps);
    print("{'''+ str(', '.join(map(str,attribute_values))) +'''}", " Histogram");
    print(arrayToString(declassify(histogram)));
    print("\\n");
}'''

    if os.path.isdir("./histogram/"):
        OUTPUT_DIR = './histogram/'
    elif os.path.isdir("../histogram/"):
        OUTPUT_DIR = '../histogram/'
    else:
        OUTPUT_DIR = './'
    with open(OUTPUT_DIR + 'histogram_main_' + main_counter + '.sc', 'w') as output:
        output.write(imports)
        output.write(main_f)
    print(good('Main generated at ' + OUTPUT_DIR + 'histogram_main_' + main_counter + '.sc'))

if __name__ == '__main__':
    main()














