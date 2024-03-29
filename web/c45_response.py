import sys
import os
import argparse
import json
import pandas as pd
from tree_response import *

parser = argparse.ArgumentParser()
parser.add_argument('c45_output', help= 'JSON file with the C4.5 output.')
parser.add_argument('configuration', help= 'Configuration file of the request.')
parser.add_argument('--summary', help = 'CSV file with the summary of the dataset.', default = 'datasets/analysis_test_data/cvi_summary.csv')
parser.add_argument('--cvi_mapping', help = 'File with the cvi categorical attributes mapping (values to integers).', default = 'datasets/analysis_test_data/cvi_mapping.json')
parser.add_argument('--plot', help = 'Flag to indicate if output should be plotted / visualized or not.', action = 'store_true')
args = parser.parse_args()

configuration = {}
cvi_mapping = {}
mins = []
maxs = []
attributes = []
class_cells = -1


def main():
    global configuration
    global cvi_mapping
    global attributes
    global class_cells
    global mins
    global maxs
    configuration = json.load(open(args.configuration))
    cvi_mapping = json.load(open(args.cvi_mapping))
    attributes = [a['name'] for a in configuration['attributes']]
    if 'cells' in configuration['class_attribute']:
        class_cells = int(configuration['class_attribute']['cells'])
    class_attribute = configuration['class_attribute']['name']
    total_attributes = attributes + [class_attribute]
    summary = pd.read_csv(args.summary, sep = ',')
    for attribute in total_attributes:
        if attribute in summary['Field'].values:
            mins.append(summary[summary['Field']==attribute][' Min'].item())
            maxs.append(summary[summary['Field']==attribute][' Max'].item())
        else:
            mins.append(0.0)
            maxs.append(0.0)
    with open(args.c45_output) as results:
        for line in results:
            if line.startswith('{'):
                tree = json.loads(line)
                preprocessed_tree = preprocess(tree)
                converted, nodes, edges, leaves, id, subtrees = convert_tree(preprocessed_tree)
                break
    if args.plot:
        class_name = configuration['class_attribute']['name']
        filename = 'graphs/c45'+'_'+str(os.getpid())+'.html'
        plotted_file = plot(nodes, edges, leaves, class_name, filename)
        print(plotted_file)
    else:
        print(json.dumps(converted))


def split_node(node):
    parts = node.split()
    attribute_index = int(parts[0])
    threshold = "{0:.2f}".format(float(parts[2]))
    operator = parts[1]
    return attribute_index, threshold, operator

def convert_tree(tree, id = 0, nodes = [], edges = [], leaves = {}, parent = '', branch = '', subtrees_map = {}):
    new_tree ={}
    class_attribute = configuration['class_attribute']['name']
    first_node = True
    graph_node_id = ''

    if str(tree) in subtrees_map:
        graph_node = subtrees_map[str(tree)]
        graph_node_id = graph_node['data']['id']
        edge_source = parent['data']['id']
        edge_target = graph_node_id
        edge_node = { 'data': { 'source': edge_source, 'target': edge_target, 'label': branch } }
        edges.append(edge_node)
        return new_tree, nodes, edges, leaves, id, subtrees_map

    if not isinstance(tree,dict): # if tree is a leaf
        if class_attribute in cvi_mapping:
            possible_values = cvi_mapping[class_attribute]
            value_name = [value for value, mapping in possible_values.items() if int(mapping) == int(float(tree))][0]
        else: 
            class_min = mins[-1]
            class_max = maxs[-1]
            value_index = int(tree)
            cell_width = (class_max - class_min) / class_cells
            start = class_min + value_index * cell_width
            end = start + cell_width
            value_name = '['+"{0:.2f}".format(start)+', '+"{0:.2f}".format(end)+')'
        subtree = value_name

        if subtree not in leaves:
            id += 1
            graph_node_id = subtree + '_' + str(id)
            graph_node_label =  subtree
            graph_node = {'data' : { 'id' : str(graph_node_id), 'label' : str(graph_node_label)} }
            nodes.append(graph_node)
            leaves[subtree] = (graph_node_id)
        else:
            graph_node_id = leaves[subtree]
        if parent != '':
            edge_source = parent['data']['id']
            edge_target = graph_node_id
            edge_node = { 'data': { 'source': str(edge_source), 'target': str(edge_target), 'label': str(branch) } }
            edges.append(edge_node)
        return subtree, nodes, edges, leaves, id, subtrees_map
    for node, subtree in tree.items():
        id += 1

        attribute_index, threshold, operator = split_node(node);
        attribute_name = str(attributes[attribute_index])
        value_name = threshold
        if attribute_name in cvi_mapping:
            possible_values = cvi_mapping[attribute_name]
            value_name = [value for value, mapping in possible_values.items() if int(mapping) == int(float(threshold))][0]
        new_node = attribute_name + ' ' + operator + ' ' + value_name

        if first_node:
            graph_node_id = attribute_name + '_' + str(id)
            graph_node_label =  attribute_name
            graph_node = {'data' : { 'id' : str(graph_node_id), 'label' : str(graph_node_label)} }
            nodes.append(graph_node)
            first_node = False
            subtrees_map[str(tree)] = graph_node

            if parent != '':
                edge_source = parent['data']['id']
                edge_target = graph_node_id
                edge_node = { 'data': { 'source': str(edge_source), 'target': str(edge_target), 'label': str(branch) } }
                edges.append(edge_node)

        if operator == '==':
            branch = str(value_name)
        else:
            branch = str(operator + ' ' + value_name)
        subtree, nodes, edges, leaves, id, subtrees_map = convert_tree(tree = subtree, id = id, nodes = nodes, edges = edges, leaves = leaves, parent = graph_node, branch = branch, subtrees_map = subtrees_map)
        new_tree[new_node] = subtree

    return new_tree, nodes, edges, leaves, id, subtrees_map

if __name__ == '__main__':
    main()