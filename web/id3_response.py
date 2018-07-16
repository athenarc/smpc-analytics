import sys
import os
import argparse
import json
from tree_response import *

parser = argparse.ArgumentParser()
parser.add_argument('id3_output', help= 'JSON file with the id3 output.')
parser.add_argument('configuration', help= 'Configuration file of the request.')
parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = 'mhmd-driver/mesh_mapping.json')
parser.add_argument('--mtrees_inverted', help = 'File with the mesh term mapping (values to integers).', default = 'mhmd-driver/m_inv.json')
parser.add_argument('--plot', help = 'Flag to indicate if output should be plotted / visualized or not.', action = 'store_true')
args = parser.parse_args()

mesh_mapping = {}
mesh_dict_inverted = {}
configuration = {}

def main():
    global mesh_mapping
    global mesh_dict_inverted
    global configuration
    mesh_mapping = json.load(open(args.mapping))
    mesh_dict_inverted = json.load(open(args.mtrees_inverted))
    configuration = json.load(open(args.configuration))
    with open(args.id3_output) as results:
        for line in results:
            if line.startswith('{'):
                tree = json.loads(line)
                print(tree)
                preprocessed_tree = preprocess(tree)
                print(preprocessed_tree)
                converted, nodes, edges, leaves, id, subtrees = convert_tree(preprocessed_tree)
                break
    if args.plot:
        class_name = mesh_dict_inverted[configuration['class_attribute']]
        filename = 'graphs/id3'+'_'+str(os.getpid())+'.html'
        plotted_file = plot(nodes, edges, leaves, class_name, filename)
        print(plotted_file)
    else:
        print(json.dumps(converted))


def convert_tree(tree, id = 0, nodes = [], edges = [], leaves = {}, parent = '', branch = '', subtrees_map = {}):
    new_tree ={}
    class_attribute_id = configuration['class_attribute']
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
        print([mesh_dict_inverted[name] for name,index in mesh_mapping[class_attribute_id].items() if index == tree])
        subtree = str([mesh_dict_inverted[name] for name,index in mesh_mapping[class_attribute_id].items() if index == tree][0])

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
        attribute_id = configuration['attributes'][attribute_index]
        attribute_name = str(mesh_dict_inverted[attribute_id])
        value_name = str([mesh_dict_inverted[name] for name,index in mesh_mapping[attribute_id].items() if index == value_index][0])
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