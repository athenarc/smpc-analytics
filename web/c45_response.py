import sys
import os
import argparse
import json
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('c45_output', help= 'JSON file with the C4.5 output.')
parser.add_argument('configuration', help= 'Configuration file of the request.')
parser.add_argument('--summary', help = 'CSV file with the summary of the dataset.', default = 'datasets/analysis_test_data/cvi_summary.csv')
parser.add_argument('--plot', help = 'Flag to indicate if output should be plotted / visualized or not.', action = 'store_true')
args = parser.parse_args()

configuration = {}
mins = []
maxs = []
attributes = []
class_cells = -1


def main():
    global configuration
    global attributes
    global class_cells
    global mins
    global maxs
    configuration = json.load(open(args.configuration))
    attributes = [a['name'] for a in configuration['attributes']]
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
                converted, nodes, edges, leaves, id = convert_tree(tree)
                break
    if args.plot:
        plotted_file = plot(nodes, edges, leaves)
        print(plotted_file)
    else:
        print(json.dumps(converted))


def split_node(node):
    parts = node.split()
    attribute_index = int(parts[0])
    threshold = "{0:.2f}".format(float(parts[2]))
    operator = parts[1]
    return attribute_index, threshold, operator

def convert_tree(tree, id = 0, nodes = [], edges = [], leaves = {}, parent = '', branch = ''):
    new_tree ={}
    class_attribute = configuration['class_attribute']['name']
    first_node = True
    graph_node_id = ''
    if not isinstance(tree,dict): # if tree is a leaf
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
        return subtree, nodes, edges, leaves, id
    for node, subtree in tree.items():
        id += 1

        attribute_index, threshold, operator = split_node(node);
        attribute_name = str(attributes[attribute_index])
        attribute_min = mins[attribute_index]
        attribute_max = maxs[attribute_index]
        new_node = attribute_name + ' ' + operator + ' ' + threshold

        if first_node:
            graph_node_id = attribute_name + '_' + str(id)
            graph_node_label =  attribute_name
            graph_node = {'data' : { 'id' : graph_node_id, 'label' : graph_node_label} }
            nodes.append(graph_node)
            first_node = False

            if parent != '':
                edge_source = parent['data']['id']
                edge_target = graph_node_id
                edge_node = { 'data': { 'source': edge_source, 'target': edge_target, 'label': branch } }
                edges.append(edge_node)

        branch = str(operator + ' ' + threshold)
        subtree,nodes,edges,leaves, id = convert_tree(tree = subtree, id = id, nodes = nodes, edges = edges, leaves = leaves, parent = graph_node, branch = branch)
        new_tree[new_node] = subtree

    return new_tree, nodes, edges, leaves, id

def plot(nodes, edges, leaves):
    class_name = configuration['class_attribute']['name']
    html = '''<!DOCTYPE>
    <html>
      <head>
        <title>Decision Tree for class '''+class_name+'''</title>
        <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1">
        <link href="style.css" rel="stylesheet" />

        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.2.11/cytoscape.js"></script>
        <script src="https://cdn.rawgit.com/cpettitt/dagre/v0.7.4/dist/dagre.min.js"></script>
        <script src="https://cdn.rawgit.com/cytoscape/cytoscape.js-dagre/1.5.0/cytoscape-dagre.js"></script>

      </head>
      <body>
        <h1>Decision Tree for class '''+class_name+'''</h1>
        <div id="cy"></div>
        <script>
          var cy = window.cy = cytoscape({
            container: document.getElementById('cy'),
            boxSelectionEnabled: false,
            autounselectify: true,

            layout: {
              name: 'dagre'
            },

            style: [
              {
                selector: 'node',
                style: {
                  'content': 'data(label)',
                  'text-opacity': 0.7,
                  'text-valign': 'center',
                  'text-halign': 'center',
                  'background-color': '#5cb85c'
                }
              },
              {
                selector: 'edge',
                style: {
                  'curve-style': 'bezier',
                  'width': 1,
                  'target-arrow-shape': 'triangle',
                  'line-color': '#d7efd7',
                  'target-arrow-color': '#d7efd7'
                }
              },
              {
                selector: 'edge',
                style: {
                  'label': '',
                  'text-opacity': 0.5
                }
              },
              {
                selector: '.edge_with_label',
                style: {
                  'label': 'data(label)',
                  'text-opacity': 0.5
                }
              },
              {
                  selector: '.leafClass',
                  style: {
                    'content': 'data(label)',
                    'text-opacity': 0.7,
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'background-color': '#EDB76B'
                  }
                }
            ],
            elements: {
                nodes: ['''
    html += str(',\n'.join(map(str,nodes)))
    html += '''],
                edges: ['''
    html += str(',\n'.join(map(str,edges)))
    html += ''']
                    },
                });
    '''
    for leaf, id in leaves.items():
        html += ''' cy.$("[id=\'''' + id + '''\']").classes('leafClass');
    '''
    html += '''
    cy.on('tap', 'edge', function(evt) {
        if (cy.$("[id='" + String(evt.target.id()) + "']").hasClass('edge_with_label')) {
            cy.$("[id='" + String(evt.target.id()) + "']").classes('edge');
        } else {
            cy.$("[id='" + String(evt.target.id()) + "']").classes('edge_with_label');
        }
    });
    '''
    html += '''</script>
          </body>
        </html>
    '''
    filename = 'graphs/c45'+'_'+str(os.getpid())+'.html'
    with open('web/' + filename, 'w') as output:
        output.write(html)
    return filename


if __name__ == '__main__':
    main()