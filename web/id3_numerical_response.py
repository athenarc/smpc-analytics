import sys
import os
import argparse
import json
import pandas as pd
from tree_response import *

parser = argparse.ArgumentParser()
parser.add_argument('id3_output', help= 'JSON file with the id3 output.')
parser.add_argument('configuration', help= 'Configuration file of the request.')
parser.add_argument('--summary', help = 'CSV file with the summary of the dataset.', default = 'datasets/analysis_test_data/cvi_summary.csv')
parser.add_argument('--plot', help = 'Flag to indicate if output should be plotted / visualized or not.', action = 'store_true')
args = parser.parse_args()

configuration = {}
mins = []
maxs = []
attributes = []
cells = []


def main():
    global configuration
    global attributes
    global cells
    global mins
    global maxs
    configuration = json.load(open(args.configuration))
    attributes = [a['name'] for a in configuration['attributes']]
    cells = [int(a['cells']) for a in configuration['attributes']] + [int(configuration['class_attribute']['cells'])]
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
    with open(args.id3_output) as results:
        for line in results:
            if line.startswith('{'):
                tree = json.loads(line)
                preprocessed_tree = preprocess(tree)
                converted, nodes, edges, leaves, id, subtrees = convert_tree(preprocessed_tree)
                break
    if args.plot:
        class_name = configuration['class_attribute']['name']
        filename = 'graphs/id3'+'_'+str(os.getpid())+'.html'
        plotted_file = plot(nodes, edges, leaves, class_name, filename)
        print(plotted_file)
    else:
        print(json.dumps(converted))


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
        attribute_min = mins[-1]
        attribute_max = maxs[-1]
        attribute_cells = cells[-1]
        value_index = int(tree)
        cell_width = (attribute_max - attribute_min) / attribute_cells
        start = attribute_min + value_index * cell_width
        end = start + cell_width
        value_name = '['+"{0:.2f}".format(start)+', '+"{0:.2f}".format(end)+')'
        subtree = value_name

        if subtree not in leaves:
            id += 1
            graph_node_id = subtree + '_' + str(id)
            graph_node_label =  subtree
            graph_node = {'data' : { 'id' : graph_node_id, 'label' : graph_node_label} }
            nodes.append(graph_node)
            leaves[subtree] = (graph_node_id)
        else:
            graph_node_id = leaves[subtree]
        if parent != '':
            edge_source = parent['data']['id']
            edge_target = graph_node_id
            edge_node = { 'data': { 'source': edge_source, 'target': edge_target, 'label': branch } }
            edges.append(edge_node)
        return subtree, nodes, edges, leaves, id, subtrees_map
    for node, subtree in tree.items():
        id += 1

        attribute_index = int(node.split(' == ')[0])
        value_index = int(node.split(' == ')[1])
        attribute_name = str(attributes[attribute_index])
        attribute_min = mins[attribute_index]
        attribute_max = maxs[attribute_index]
        attribute_cells = cells[attribute_index]
        cell_width = (attribute_max - attribute_min) / attribute_cells
        start = attribute_min + value_index * cell_width
        end = start + cell_width
        value_name = '['+"{0:.2f}".format(start)+', '+"{0:.2f}".format(end)+')'
        new_node = attribute_name + ' == ' + value_name

        if first_node:
            graph_node_id = attribute_name + '_' + str(id)
            graph_node_label =  attribute_name
            graph_node = {'data' : { 'id' : graph_node_id, 'label' : graph_node_label} }
            nodes.append(graph_node)
            first_node = False
            subtrees_map[str(tree)] = graph_node

            if parent != '':
                edge_source = parent['data']['id']
                edge_target = graph_node_id
                edge_node = { 'data': { 'source': edge_source, 'target': edge_target, 'label': branch } }
                edges.append(edge_node)

        subtree, nodes, edges, leaves, id, subtrees_map = convert_tree(tree = subtree, id = id, nodes = nodes, edges = edges, leaves = leaves, parent = graph_node, branch = value_name, subtrees_map = subtrees_map)
        new_tree[new_node] = subtree
    return new_tree, nodes, edges, leaves, id, subtrees_map

if __name__ == '__main__':
    main()