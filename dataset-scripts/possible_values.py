from __future__ import print_function
import csv
import json
import os
import pandas

OUTPUT_FILE = 'mesh_mapping.json'

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
    mesh_dict = construct_dict('../datasets/mtrees2018.csv') # name -> code
    mesh_dict_inverted = construct_dict('../datasets/mtrees2018_inverted.csv') # code -> name
    direct_children = {}

    for term in mesh_dict.keys():
        code = mesh_dict[term]
        depth = mesh_tree_depth(code)
        children = len([key for key in mesh_dict_inverted.keys() if key.startswith(code) and mesh_tree_depth(key) == depth + 1])
        direct_children[term] = children
        # print(term+': --> '+str(children))

    with open(OUTPUT_FILE, 'w') as outfile:
        json.dump(direct_children, outfile)

if __name__ == '__main__':
    main()
