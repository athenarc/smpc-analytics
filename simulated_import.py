import argparse
import sys
import json
import pandas as pd
import os
from subprocess import Popen, PIPE, STDOUT
from huepy import *
import hashlib

class ProcessError(Exception):
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message

def execute(command, stdout, stdin, stderr, verbose=False):
    if verbose:
        # print('[INFO] Running: ' + ' '.join(command))
        print(run('Running: ' + ' '.join(command) +' from '+ os.path.dirname(os.path.realpath(__file__))))
    process = Popen(command, stdout=stdout, stdin = stdin, stderr = stderr, cwd=os.path.dirname(os.path.realpath(__file__)))
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
    parser.add_argument('--float', help= 'Optional argument to force all columns have type float64', action='store_true')
    parser.add_argument('--verbose', help = 'See executed commands in verbose output', action = 'store_true')
    args = parser.parse_args()

    build_secrec_script(args.file, args.table, args.float, args.verbose)

    try:
        execute(["sharemind-scripts/compile.sh", "simulated_import.sc"], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
    except ProcessError as e:
        print(bad('Error in secrec compilation'))
        return 1

    try:
        execute(["sharemind-scripts/run.sh", "simulated_import.sb"], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
    except ProcessError as e:
        print(bad('Error in secrec execution'))
        return 1

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

def build_secrec_script(data, table, float, verbose):
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
    main_f += '''
    string datasource = "DS1";
    string table = ''' + quote(table_name) + ''';
    uint64 rows = ''' + quote(len(df.index)) + ''';
    uint64 columns = ''' + quote(len(df.columns)) + ''';
'''
    imported_array = []
    for index, row in df.iterrows():
        imported_array += [row[i] for i in df.columns]

    main_f += '''
    pd_shared3p int64[[2]] imported_array = reshape({''' + ','.join(map(str,imported_array)) + '''}, rows, columns);
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
        if float:
            infered_type = 'float64'
        else:
            infered_type = str(df[attribute].dtype)
        main_f += '''
    pd_shared3p ''' + infered_type + ''' v''' + str(i) + ''';
    tdbVmapAddType(parameters, "types", v''' + str(i) + ''');
    tdbVmapAddString(parameters, "names", ''' + quote(attribute) + ''');
'''
        i += 1

    main_f += '''
    tdbTableCreate(datasource, table, parameters);
    print("Inserting data to table " + table + "...");
    pd_shared3p int64[[1]] row;
    for (uint i = 0; i < nrows; ++i) {
        row = imported_array[i,:];
        tdbInsertRow(datasource, table, row);
    }
    print("Done inserting in table " + table + "\\n\\n");


    tdbCloseConnection(datasource);
}'''

    with open('simulated_import.sc', 'w') as output:
        output.write(imports)
        output.write(main_f)
    if verbose:
        print(info('Secrec import script generated at simulated_import.sc'))



if __name__ == '__main__':
    main()
