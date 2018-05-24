import sys
import json
import argparse
import operator
import itertools
import numpy
from huepy import *

parser = argparse.ArgumentParser()
parser.add_argument('configuration', help= 'Configuration file of the request.')
parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = '../datasets/mesh_mapping.json')
args = parser.parse_args()

with open (args.configuration) as configuration:
    configuration = json.loads(configuration.readline())
    line = json.loads(sys.stdin.readline())
    mesh_mapping = json.load(open(args.mapping))
    attributes = configuration['attributes']
    possible_values = [mesh_mapping[attribute] for attribute in attributes]
    possible_values = [[str(k) for k,v in sorted(values.items(), key=operator.itemgetter(1))] for values in possible_values]
    cellsPerDimension = line[0]['cellsPerDimension']
    histogram = line[0]['histogram']
    if numpy.product(cellsPerDimension) != len(histogram):
        print(bad('histogram length and possible_values do not match!'))
        sys.exit(1)
    # for dimension in reversed(cellsPerDimension[1:]):
    #     histogram = [histogram[i:i+dimension] for i in xrange(0, len(histogram), dimension)]
    output = {'data' : []}
    i = 0
    if len(possible_values) == 1:
        for p in possible_values[0]:
            tuple = {'label' : str(p), 'value' : histogram[i]}
            output['data'].append(tuple)
            i += 1
    else:
        for p in itertools.product(*possible_values):
            tuple = {'label' : str(p), 'value' : histogram[i]}
            output['data'].append(tuple)
            i += 1
    print(json.dumps(output))
