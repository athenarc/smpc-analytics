import sys
import json
import argparse
import operator

parser = argparse.ArgumentParser()
parser.add_argument('configuration', help= 'Configuration file of the request.')
parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = '../datasets/mesh_mapping.json')
args = parser.parse_args()

with open (args.configuration) as configuration:
    configuration = json.loads(configuration.readline())
    line = json.loads(sys.stdin.readline())
    mesh_mapping = json.load(open(args.mapping))
    attribute = configuration['attribute']
    possible_values = mesh_mapping[attribute]
    possible_values = [str(k) for k,v in sorted(possible_values.items(), key=operator.itemgetter(1))]
    # cellsPerDimension = line[0]['cellsPerDimension'][0]
    histogram = line[0]['histogram']
    if len(possible_values) != len(histogram):
        print('histogram length and possible_values do not match!')
        sys.exit(1)
    output = {'data' : []}
    for i in range(len(histogram)):
        tuple = {'label' : possible_values[i], 'value' : histogram[i]}
        output['data'].append(tuple)
    print(json.dumps(output))