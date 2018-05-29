from __future__ import print_function
import json
import os
import argparse
from huepy import *

parser = argparse.ArgumentParser()
parser.add_argument('--mtrees', help = 'File with the mesh term mapping (values to integers).', default = '/m.json')
parser.add_argument('--mtrees_inverted', help = 'File with the mesh term mapping (values to integers).', default = '/m_inv.json')
parser.add_argument('--output', help = 'The output csv to be created.', default = '../datasets/mesh_mapping.json')
parser.add_argument('--verbose', help = 'See verbose output', action = 'store_true')
args = parser.parse_args()

def mesh_tree_depth(id):
    if len(id) == 1:
        return 0
    else:
        return id.count('.') + 1

def main():
    mesh_dict = json.load(open(args.mtrees))
    mesh_dict_inverted = json.load(open(args.mtrees_inverted))
    direct_children = {}

    print(run('Generating Mesh mapping..'))
    for id in mesh_dict_inverted.keys():
        depth = mesh_tree_depth(id)
        children_ids = [key for key in mesh_dict_inverted.keys() if key.startswith(id) and mesh_tree_depth(key) == depth + 1]
        childred_mapping = dict((id , i) for i,id in enumerate(children_ids) )
        direct_children[id] = childred_mapping
        if args.verbose:
            print(info(id+': --> '+str(childred_mapping)))

    with open(args.output, 'w') as outfile:
        json.dump(direct_children, outfile)

    print(good('Mesh mapping generated successfully.'))

if __name__ == '__main__':
    main()
