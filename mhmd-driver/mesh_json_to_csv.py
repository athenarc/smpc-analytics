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
parser.add_argument('--mtrees', help = 'File with the mesh term mapping (values to integers).', default = '/m.json')
parser.add_argument('--mtrees_inverted', help = 'File with the mesh term mapping (values to integers).', default = '/m_inv.json')
parser.add_argument('--output', help = 'The output csv to be created.', default = '/data.csv')
parser.add_argument('--verbose', help = 'See verbose output', action = 'store_true')
args = parser.parse_args()


def print_branch(id, mesh_dict_inverted):
    mesh_branch = id.split('.')
    mesh_branch_ids = ['.'.join(mesh_branch[:i]) for i in range(1,len(mesh_branch)+1)]
    mesh_branch_names = [mesh_dict_inverted[id] for id in mesh_branch_ids]
    top_level_id = mesh_branch_ids[0][0]
    top_level_name = mesh_dict_inverted[top_level_id]
    mesh_branch_names = [top_level_name] + mesh_branch_names
    print(info(yellow('** ') + ' -> '.join(mesh_branch_names)))

def mesh_tree_depth(id):
    if len(id) == 1:
        return 0
    else:
        return id.count('.') + 1

def main():
    mesh_dict = json.load(open(args.mtrees))
    mesh_dict_inverted = json.load(open(args.mtrees_inverted))
    mesh_mapping = json.load(open(args.mapping))
    MESH_TERM_IDS = args.attributes.split()
    MESH_TERM_NAMES = [mesh_dict_inverted[id] for id in MESH_TERM_IDS]
    direct_children = {}

    for term,id in zip(MESH_TERM_NAMES, MESH_TERM_IDS):
        if term not in mesh_dict or id not in mesh_dict_inverted:
            print(bad('Wrong Mesh term: "' + term + ' [' + id + ']"'))
            sys.exit(1)
        code = mesh_dict[term]['code']
        depth = mesh_tree_depth(id)
        children = [key for key in mesh_dict_inverted.keys() if key.startswith(id) and mesh_tree_depth(key) == depth + 1]
        direct_children[id] = children


    df = pandas.DataFrame(columns = MESH_TERM_IDS)
    for filename in os.listdir(args.patient_directory): # for each patient file
        patient_values = OrderedDict([(key, [-1]) for key in MESH_TERM_IDS]) # initialize values to list with null value (-1), for every id in MESH_TERM_IDS. Keep insertion order.
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
                        if name not in mesh_dict: # Missing key case. Should be further investigated. Continue for now.
                            continue
                        if args.verbose:
                            print(info(''))
                            print(info('Name: '+ name))
                        ids = mesh_dict[name]['ids'] # Each name/code has multiple ids
                        id_found = False
                        for keyword_id in ids: # Iterate over each id. If a match is found break.
                            if args.verbose:
                                print(info(yellow('* ') +'ID: '+ keyword_id))
                                print_branch(keyword_id, mesh_dict_inverted)

                            for mesh_id in MESH_TERM_IDS:
                                children = direct_children[mesh_id]
                                for child in children:
                                    if child in keyword_id: # If child is a substring of keyword_id
                                        id_found = True # We found a matching id. No need to check for the rest.
                                        mapped_value = mesh_mapping[mesh_id][child]
                                        if patient_values[mesh_id] == [-1]:
                                            patient_values[mesh_id] = [mapped_value]
                                        else:
                                            patient_values[mesh_id].append(mapped_value)
                                        break
                            if id_found:
                                break

        if args.verbose:
            print(info(dict(patient_values)))
            print(yellow('-----------------------------------------------------------------------------------------------------'))
        for product in [zip(MESH_TERM_IDS, p) for p in itertools.product(*[values for key,values in patient_values.items()])]: # cartesian product of all attribute values
            df = df.append(dict(product), ignore_index = True)

    df.fillna(-1, inplace = True)

    if df.empty:
        df = df.append({id: -1 for id in MESH_TERM_IDS}, ignore_index = True)

    df = df.astype(int)

    df.to_csv(args.output, sep = ',', index = False)
    print(good('CSV file generated successfully at ' + args.output))

if __name__ == '__main__':
    main()
