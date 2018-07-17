def preprocess(tree):
    fix_point = False
    while not fix_point:
        new_tree = preprocess_tree(tree)
        if new_tree == tree:
            fix_point = True
        tree = new_tree
    return tree

def preprocess_tree(tree):
    if not isinstance(tree,dict):
        return tree

    tree = {node: preprocess_tree(subtree) for node, subtree in tree.items()}
    allSubtrees = [str(subtree) for node, subtree in tree.items()]
    if allEqual(allSubtrees):
        subtree = allSubtrees[0]
        return subtree
    return tree

def allEqual(iterator):
    return len(set(iterator)) <= 1


def plot(nodes, edges, leaves, class_name, filename, postprocess = True):
    if postprocess:
        edge_map = {}
        for edge in edges:
            key = edge['data']['source'] + edge['data']['target']
            if key not in edge_map:
                edge_map[key] = edge
            else:
                edge_map[key]['data']['label'] += '\n' + edge['data']['label']
        edges = list(edge_map.values())
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
                  'text-wrap' : 'wrap',
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
    with open('web/' + filename, 'w') as output:
        output.write(html)
    return filename

if __name__ == '__main__':
    main()