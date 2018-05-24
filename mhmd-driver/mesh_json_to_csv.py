from __future__ import print_function
import csv
import json
import os
import pandas
import argparse
import itertools
from huepy import *
import sys
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument('attributes', help = 'Attributes of the request')
parser.add_argument('--patient_directory', help = 'Directory of the patient .json files.', default = '/patient_files')
parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = '/mesh_mapping.json')
parser.add_argument('--mtrees', help = 'File with the mesh term mapping (values to integers).', default = '/mtrees2018.csv')
parser.add_argument('--mtrees_inverted', help = 'File with the mesh term mapping (values to integers).', default = '/mtrees2018_inverted.csv')
parser.add_argument('--output', help = 'The output csv to be created.', default = '/data.csv')
parser.add_argument('--verbose', help = 'See verbose output', action = 'store_true')
args = parser.parse_args()


def construct_dict(csv_file, delimiter=';'):
    with open(csv_file) as f:
        reader = csv.reader(f, skipinitialspace=True, delimiter=delimiter)
        d = dict(reader)
        return d

def mesh_tree_depth(code):
    if len(code) == 1:
        return 0
    else:
        return code.count('.') + 1

def main():
    MESH_TERMS = args.attributes.split(',')
    mesh_dict = construct_dict(args.mtrees) # name -> code
    mesh_dict_inverted = construct_dict(args.mtrees_inverted) # code -> name
    mesh_mapping = json.load(open(args.mapping))
    direct_children = {}

    for term in MESH_TERMS:
        if term not in mesh_dict:
            print(bad('Wrong Mesh term: "' + term + '"'))
            sys.exit(1)
        code = mesh_dict[term]
        depth = mesh_tree_depth(code)
        children = [mesh_dict_inverted[key] for key in mesh_dict_inverted.keys() if key.startswith(code) and mesh_tree_depth(key) == depth + 1]
        direct_children[term] = children


    df = pandas.DataFrame(columns = MESH_TERMS)
    for filename in os.listdir(args.patient_directory): # for each patient file
        patient_values = OrderedDict([(key, [-1]) for key in MESH_TERMS]) # initialize values to list with null value (-1), for every term in MESH_TERMS. Keep insertion order.
        if filename.endswith('.json'):
            full_name = os.path.join(args.patient_directory, filename)
            with open(full_name) as patient_file:
                if args.verbose:
                    print(info('File: '+filename))
                patient_json = json.load(patient_file)
                keywords = patient_json['keywords']
                for keyword in keywords: # for each one of the patient's keywords
                    if keyword['valueIRI'].startswith('https://meshb.nlm.nih.gov'):
                        name = keyword['value']
                        code = mesh_dict[name]
                        mesh_branch = code.split('.')
                        mesh_branch_codes = ['.'.join(mesh_branch[:i]) for i in range(1,len(mesh_branch)+1)]
                        mesh_branch_names = [mesh_dict_inverted[code] for code in mesh_branch_codes]

                        top_level_code = mesh_branch_codes[0][0]
                        top_level_name = mesh_dict_inverted[top_level_code]
                        mesh_branch_names = [top_level_name] + mesh_branch_names
                        if args.verbose:
                            print(info(yellow('* ') + ' -> '.join(mesh_branch_names)))
                        for term in MESH_TERMS:
                            children = direct_children[term]
                            value = set(mesh_branch_names).intersection(children)
                            if len(value) > 0:
                                value = str(list(value)[0])
                                mapped_value = mesh_mapping[term][value]
                                if patient_values[term] == [-1]:
                                    patient_values[term] = [mapped_value]
                                else:
                                    patient_values[term].append(mapped_value)

        if args.verbose:
            print(info(dict(patient_values)))
            print(yellow('-----------------------------------------------------------------------------------------------------'))
        for product in [zip(MESH_TERMS, p) for p in itertools.product(*[values for key,values in patient_values.items()])]: # cartesian product of all attribute values
            df = df.append(dict(product), ignore_index = True)

    df.fillna(-1, inplace = True)

    if df.empty:
        df = df.append({term: -1 for term in MESH_TERMS}, ignore_index = True)

    df = df.astype(int)

    df.to_csv(args.output, sep = ',', index = False)
    print(good('CSV file generated successfully at ' + args.output))

if __name__ == '__main__':
    main()
