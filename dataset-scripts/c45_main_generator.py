import ast
import sys
import json
from huepy import *
import os.path
import argparse
import pandas as pd

indentation = '    '

imports = '''
import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

import oblivious;
import shared3p_oblivious;

import shared3p_table_database;
import table_database;
import c45_db;
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

    parser = argparse.ArgumentParser()
    parser.add_argument('configuration', help = 'Configuration file of the request')
    parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = 'mhmd-driver/mesh_mapping.json')
    parser.add_argument('--summary', help = 'CSV file with the summary of the dataset.', default = 'datasets/analysis_test_data/cvi_summary.csv')
    parser.add_argument('--DNS', help = 'File with the Hospitals names and IPS.', default = 'web/MHMDdns.json')
    args = parser.parse_args()

    print(run('Generating main..'))

    uid = args.configuration.split('_')[-1].split('.')[0]
    configuration = json.load(open(args.configuration))
    mapping = json.load(open(args.mapping))
    summary = pd.read_csv(args.summary, sep = ',')

    if 'datasources' in configuration:
        numberOfDatasets = len(configuration['datasources'])
        data_providers = '\n'.join([indentation + "string table_" + quote(i) + " = " + quote(configuration['datasources'][i] + '_' + uid) + ";" for i in range(len(configuration['datasources']))])
    else:
        dns = json.load(open(args.DNS))
        available_datasources = dns.keys()
        numberOfDatasets = len(available_datasources)
        data_providers = '\n'.join([indentation + "string table_" + quote(i) + " = " + quote(available_datasources[i] + '_' + uid) + ";" for i in range(len(available_datasources))])

    main_f += data_providers
    main_f += '''
    // Create the data-providers list
    providers_vmap = tdbVmapNew();
    data_providers_num = ''' + quote(numberOfDatasets) + ''';
'''
    for i in range(numberOfDatasets):
        main_f += '''
    tdbVmapAddString(providers_vmap, "0", table_'''+ quote(i) +''');
'''
    attributes = configuration['attributes']
    class_attribute = configuration['class_attribute']['name']
    original_attributes = list(range(len(attributes)+1))
    class_index = len(attributes)
    main_f += '''
    original_attributes = {'''+','.join(map(quote,original_attributes))+'''};
    uint64[[1]] original_attributes_without_class = {'''+','.join(map(quote,original_attributes[:-1]))+'''};
    class_index = ''' + quote(class_index) + ''';
    possible_values = tdbVmapNew();
    float64[[1]] values;
'''


    columns = len(attributes) + 1
    main_f += '''
    columns = ''' + quote(columns) + ''';
'''
    if 'cells' in configuration['class_attribute']:
        categorical_attributes = [-1]
        class_min = summary[summary['Field'] == class_attribute][' Min'].item()
        class_max = summary[summary['Field'] == class_attribute][' Max'].item()
        class_cells = int(configuration['class_attribute']['cells'])
        main_f += '''
    values = {''' + ','.join(map(quote, list(range(class_cells)))) + '''};
    tdbVmapAddValue(possible_values, "''' + quote(class_index) + '''", values);
 '''
    else:
        categorical_attributes = [class_index]
        class_min = -1
        class_max = -1
        class_cells = -1

    main_f += '''
    categorical_attributes = {''' + ','.join(map(quote,categorical_attributes)) + '''};
    class_min = ''' + quote(class_min) + ''';
    class_max = ''' + quote(class_max) + ''';
    class_cells = ''' + quote(class_cells) + ''';
 '''
    main_f += '''
    // Open connection to DB and Insert data to different tables
    datasource = "DS1";
    print("Opening connection to db: ", datasource);
    tdbOpenConnection(datasource);

    uint64 original_example_indexes_vmap = tdbVmapNew();
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        uint64 rows = tdbGetRowCount(datasource, table);
        pd_shared3p int64[[1]] original_example_indexes(rows);
        original_example_indexes = 1;
        tdbVmapAddValue(original_example_indexes_vmap, "0", original_example_indexes);
    }
'''

    main_f += '''
    print("Running C4.5 ...");
    string root = c45(original_example_indexes_vmap, original_attributes_without_class);
    print(root);

    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        // Check if a table exists
        if (tdbTableExists(datasource, table)) {
          // Delete existing table
          print("Deleting table: ", table);
          tdbTableDelete(datasource, table);
        }
    }
}'''

    if os.path.isdir("./decision-tree/"):
        OUTPUT_DIR = './decision-tree/'
    elif os.path.isdir("../decision-tree/"):
        OUTPUT_DIR = '../decision-tree/'
    else:
        OUTPUT_DIR = './'
    with open(OUTPUT_DIR + 'main_' + uid + '.sc', 'w') as output:
        output.write(imports)
        output.write(main_f)
    print(good('Main generated at ' + OUTPUT_DIR + 'main_' + uid + '.sc'))



if __name__ == '__main__':
    main()
