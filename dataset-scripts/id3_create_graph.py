from __future__ import print_function
import pandas as pd
import numpy as np
import json
import os.path


json_file = '../ID3/id3_out.json'

INITIAL_DATASET = '../datasets/analysis_test_data/cvi_identified_100_filtered_edited.csv'
DIRECTORY, INITIAL_BASENAME = os.path.split(INITIAL_DATASET)
INITIAL_BASENAME = os.path.splitext(INITIAL_BASENAME)[0]
SERIALIZED = DIRECTORY + '/' + INITIAL_BASENAME + '_mapped_values.json'
REQ_ID = 0

# global vars, used in recursion
cnt = 0
nodes_set = set()
out = ""
leaves = {} 

def main():
    global leaves
    json_obj = json.load(open(json_file))
    map_file = open(SERIALIZED)
    attribute_map = json.load(map_file)
    df = pd.read_csv(INITIAL_DATASET, sep=',')
    id_from_node(df, attribute_map, json_obj, 0)
    
    html = '''<!DOCTYPE>
    <html>
      <head>
        <title>Labels demo</title>
        <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1">
        <link href="style.css" rel="stylesheet" />

        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.2.11/cytoscape.js"></script>
        <script src="https://cdn.rawgit.com/cpettitt/dagre/v0.7.4/dist/dagre.min.js"></script>
        <script src="https://cdn.rawgit.com/cytoscape/cytoscape.js-dagre/1.5.0/cytoscape-dagre.js"></script>

      </head>
      <body>
        <h1>Labels demo</h1>
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
                  'width': 2,
                  'target-arrow-shape': 'triangle',
                  'line-color': '#d7efd7',
                  'target-arrow-color': '#d7efd7'
                }
              },
              {
                selector: 'edge',
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
              nodes: [\n'''
    for n in nodes_set:
        html += "{ data: { id: '" + n + "', label: '" + n.split('_')[0] + "' } },\n"
    html += '''],
                    edges: [\n'''
    html += out
    # .split('\n', 1)[-1]
    html += ''']
                },
            });\n'''
    for key, val in leaves.items():
        html += val
    html += '''</script>
      </body>
    </html>
    '''
    with open('web/graphs/id3_' + str(REQ_ID) + '.html','w') as output:
        output.write(html)
    print('Created file: web/graphs/id3_' + str(REQ_ID) + '.html')

    

def id_from_node(df, attribute_map, json_obj, tabs):
    global cnt
    global nodes_set
    global out
    global leaves
    cnt += 1
    id = cnt
    src = ""
    label = ""
    for key in json_obj:
        value = json_obj[key]
        parts = key.split(" == ")
        src = parts[0]
        label = parts[1]
        # Update nodes-set
        n = df.columns[int(src)]+"_"+str(id)
        if n not in nodes_set:
            nodes_set.add(n)
        if not isinstance(value, int):
            target = id_from_node(df, attribute_map, value, tabs+1)
            # for i in range(tabs):
            #     print(end='\t')
            # print("source: '" + df.columns[int(src)]+"_"+str(id) + "', target: '" + df.columns[int(target[0])] + target[1], end="', ")
            out += "{ data: { source: '" + df.columns[int(src)]+"_"+str(id) + "', target: '" + df.columns[int(target[0])] + target[1] + "', "
        else:
            mapped_values = attribute_map[df.columns[-1]]
            val = getValue(mapped_values, value)[0]
            # Update nodes-set
            if val not in nodes_set:
                nodes_set.add(val)
            # for i in range(tabs):
            #     print(end='\t')
            # print("source: " + df.columns[int(src)]+"_"+str(id) + " target: " + val, end=" ")
            out += "{ data: { source: '" + df.columns[int(src)]+"_"+str(id) + "', target: '" + val + "', "
            leaves[val] = "cy.$(\"[id='" + val + "']\").classes('leafClass');\n"
            
        mapped_values = attribute_map[df.columns[int(src)]]
        label = getValue(mapped_values, int(label))[0]
        # print("label: '" + label + "'")
        out += "label: '" + label + "' } },\n"
    return [src, "_"+str(id)]
        
def getValue(dict, value):
     return [key for key in dict.keys() if (dict[key] == value)]
     
if __name__ == '__main__':
    main()
