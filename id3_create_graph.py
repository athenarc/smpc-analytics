#!/usr/bin/python
from __future__ import print_function
import pandas as pd
import numpy as np
import os.path
import sys
import json

req_id = '0'

if len(sys.argv) > 1:
    ID3_RESULTS = sys.argv[1]
    INITIAL_DATASET = sys.argv[2]
    req_id = sys.argv[3]
else:
    ID3_RESULTS = 'syndata_upload_and_scaling_tests/id3.out'
    INITIAL_DATASET = 'syndata_upload_and_scaling_tests/centricity_identified_filtered_edited.csv'

# Directory and name of json file
DIRECTORY, INITIAL_BASENAME = os.path.split(INITIAL_DATASET)
INITIAL_BASENAME = os.path.splitext(INITIAL_BASENAME)[0]
SERIALIZED = DIRECTORY + '/' + INITIAL_BASENAME + '_mapped_values.json'

# Directory and name of id3 results file
DIRECTORY, ID3_BASENAME = os.path.split(ID3_RESULTS)
ID3_BASENAME = os.path.splitext(ID3_BASENAME)[0]


def main():
    map_file = open(SERIALIZED)
    attribute_map = json.load(map_file)
    df = pd.read_csv(INITIAL_DATASET, sep=',')
    data_file = open(ID3_RESULTS)

    prev_word = ""
    prev_attribute = ""
    tabs = 0
    out = ""
    nodes_set = set()
    incr_lst = [0 for i in range(100000)]
    flag = False
    for line in data_file:
        for word in line.split():
            if "{" == word :
                tabs +=1
                incr_lst[tabs] += 1
                flag = True
            elif "}" == word :
                tabs -=1
            elif "[" in prev_word:
                prev_attribute = df.columns[int(word)]
                if flag:
                    out += ", target: '" + prev_attribute + '_' + str(incr_lst[tabs]) + "' } },\n{ data: { source: '" + prev_attribute + '_' + str(incr_lst[tabs]) + "'";
                else:
                    out += "\n{ data: { source: '" + prev_attribute + '_' + str(incr_lst[tabs]) + "'";
                flag = False
                if prev_attribute + '_' + str(incr_lst[tabs]) not in nodes_set:
                    nodes_set.add(prev_attribute + '_' + str(incr_lst[tabs]))
            elif "==" == prev_word:
                mapped_values = attribute_map[prev_attribute]
                val = getValue(mapped_values, int(word))[0]
                out += ", label: '" + val + "'"
            elif "-->" == prev_word and '[' not in word and '}' not in word and '{' not in word:
                mapped_values = attribute_map[df.columns[-1]]
                val = getValue(mapped_values, int(word))[0]
                out += ", target: '" + val + "' } },"
                if val not in nodes_set:
                    nodes_set.add(val)
            prev_word = word

    map_file.close()
    data_file.close()

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
              }
            ],

            elements: {
              nodes: [\n'''

    for n in nodes_set:
        html += "{ data: { id: '" + n + "', label: '" + n.split('_')[0] + "' } },\n"
    html += '''],
                    edges: [\n'''
    html += out.split('\n', 1)[-1]
    html += ''']
                },
            });
        </script>
      </body>
    </html>
    '''
    with open('web/graphs/id3_' + str(req_id) + '.html','w') as output:
        output.write(html)
    print('Created file: web/graphs/id3_' + str(req_id) + '.html')

def getValue(dict, value):
     return [key for key in dict.keys() if (dict[key] == value)]

if __name__ == '__main__':
    main()
