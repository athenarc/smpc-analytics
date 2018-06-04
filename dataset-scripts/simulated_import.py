import argparse
import sys
import json
import pandas as pd
import os
from subprocess import Popen, PIPE, STDOUT
from huepy import *
import hashlib

CURRENT_FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

class ProcessError(Exception):
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message

def execute(command, stdout, stdin, stderr, verbose=False):
    if verbose:
        # print('[INFO] Running: ' + ' '.join(command))
        print(run('Running: ' + ' '.join(command) +' from '+ CURRENT_FILE_DIRECTORY))
    process = Popen(command, stdout=stdout, stdin = stdin, stderr = stderr, cwd = CURRENT_FILE_DIRECTORY)
    out, err = process.communicate();
    rc = process.returncode
    if rc != 0:
        if verbose:
            print(out)
        raise ProcessError()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help = 'CSV file to be imported')
    parser.add_argument('--table', help= 'Optional table name')
    parser.add_argument('--attributes', help = 'Optional argument. A subset of the CSV columns only which will be imported. Semi-colon separated column names.')
    parser.add_argument('--verbose', help = 'See executed commands in verbose output', action = 'store_true')
    args = parser.parse_args()

    secrec_filename = 'simulated_import_' + str(os.getpid())
    secrec_source = secrec_filename + '.sc'
    secrec_executable =secrec_filename + '.sb'

    build_secrec_script(args.file, args.table, args.verbose, args.attributes, secrec_source)

    try:
        execute(['../sharemind-scripts/compile.sh',os.path.relpath(secrec_source, CURRENT_FILE_DIRECTORY)], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
    except ProcessError as e:
        print(bad('Error in secrec compilation'))
        sys.exit(-1)

    try:
        execute(['../sharemind-scripts/run.sh', os.path.relpath(secrec_executable, CURRENT_FILE_DIRECTORY)], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
    except ProcessError as e:
        print(bad('Error in secrec execution'))
        sys.exit(-1)

    print(good('Data successfully imported.'))


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

def build_secrec_script(data, table, verbose, columns, secrec_source = 'simulated_import.sc'):
    indentation = '    '

    imports = '''
import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;

import shared3p_table_database;
import table_database;

domain pd_shared3p shared3p;

'''
    main_f = '''
    void main(){
'''

    directory, basename = os.path.split(data)
    basename = os.path.splitext(basename)[0]

    table_name = basename
    if table != None:
        table_name = table

    df=pd.read_csv(data,sep=',')
    if columns != None:
        df = df [columns.split(';')]
    main_f += '''
    string datasource = "DS1";
    string table = ''' + quote(table_name) + ''';
    uint64 rows = ''' + quote(len(df.index)) + ''';
    uint64 columns = ''' + quote(len(df.columns)) + ''';
'''
    imported_array = []
    for index, row in df.iterrows():
        imported_array += [row[i] for i in df.columns]

    data_type = 'float64'
    main_f += '''
    pd_shared3p  ''' + data_type + '''[[2]] imported_array = reshape({''' + ','.join(map(str,imported_array)) + '''}, rows, columns);
    print("Opening connection to db: ", datasource);
    tdbOpenConnection(datasource);

    print("Table: " + table);

    // Check if a table exists
    if (tdbTableExists(datasource, table)) {
      // Delete existing table
      print("Deleting existing table: ", table);
      tdbTableDelete(datasource, table);
    }

    print("Creating new table: ", table);
    uint64 nrows = shape(imported_array)[0];
    uint64 ncols = shape(imported_array)[1];

    uint64 parameters = tdbVmapNew();
'''
    i = 0
    for attribute in df.columns:
        main_f += '''
    pd_shared3p ''' + data_type + ''' v''' + str(i) + ''';
    tdbVmapAddType(parameters, "types", v''' + str(i) + ''');
    tdbVmapAddString(parameters, "names", ''' + quote(attribute) + ''');
'''
        i += 1

    main_f += '''
    tdbTableCreate(datasource, table, parameters);
    print("Inserting data to table " + table + "...");
    pd_shared3p  ''' + data_type + '''[[1]] row;
    for (uint i = 0; i < nrows; ++i) {
        row = imported_array[i,:];
        tdbInsertRow(datasource, table, row);
    }
    print("Done inserting in table " + table + "\\n\\n");


    tdbCloseConnection(datasource);
}'''

    with open(secrec_source, 'w') as output:
        output.write(imports)
        output.write(main_f)
    if verbose:
        print(good('Secrec import script generated at '+secrec_source))



if __name__ == '__main__':
    main()
