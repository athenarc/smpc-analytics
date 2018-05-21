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
    print('Generating main..')

    if len(sys.argv) > 1:
        configuration = sys.argv[1]
        if len(sys.argv) > 2:
            mesh_mapping = sys.argv[2]
        else:
            mesh_mapping = 'datasets/mesh_mapping.json'
    else:
        print('No arguement provided')
        sys.exit(1)

    main_counter = configuration.split('_')[-1].split('.')[0]

    configuration = json.load(open(configuration))
    mapping = json.load(open(mesh_mapping))


    if 'datasources' in configuration:
        numberOfDatasets = len(configuration['datasources'])
        data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(configuration['datasources'][i]) + ";" for i in range(len(configuration['datasources']))])
    else:
        numberOfDatasets = len(available_datasources)
        data_providers = '\n'.join([indentation + "string table_" + str(i) + " = " + quote(available_datasources[i]) + ";" for i in range(len(available_datasources))])

    attribute = configuration['attribute']
    attribute_values = len(mapping[attribute])

    main_f += '''
    string column_name = "'''+ attribute +'''";
    uint64 P = '''+ str(attribute_values) +''';
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
    print("Computing histogram");
'''
    main_f += '''
    pd_shared3p uint64[[1]] histogram = histogram_categorical(datasource, providers_vmap, data_providers_num, column_name, P);
    print("{''' + str(attribute_values) + '''}", " Histogram");
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

if __name__ == '__main__':
    main()














