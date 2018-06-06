import sys
import os
import argparse
import operator
import json
import plotly
import plotly.graph_objs as go

parser = argparse.ArgumentParser()
parser.add_argument('count_output', help= 'Text file with the count computation output.')
parser.add_argument('configuration', help= 'Configuration file of the request.')
parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = '../mhmd-driver/mesh_mapping.json')
parser.add_argument('--mtrees_inverted', help = 'File with the mesh term mapping (values to integers).', default = '../mhmd-driver/m_inv.json')
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
    attributes = configuration['attributes']
    possible_values = [mesh_mapping[attribute] for attribute in attributes]
    possible_values = [[str(k) for k,v in sorted(values.items(), key=operator.itemgetter(1))] for values in possible_values]
    with open(args.count_output) as results:
        for line in results:
            if line.startswith('{') and 'Histogram' in line:
                dimensions = [int(x) for x in (line[1:-(len('Histogram')+3)]).split(', ')]
                histogram = [int(x) for x in (next(results)[1:-2]).split(', ')]
                if len(dimensions) == 1 or (len(dimensions) == 2 and 1 in dimensions):
                    data = [go.Bar(y=histogram)]
                    if len(configuration['attributes']) == 1:
                        attribute_id = configuration['attributes'][0]
                        attribute_name = mesh_dict_inverted[attribute_id]
                        ticks = [str(mesh_dict_inverted[k]) for k,v in sorted(mesh_mapping[attribute_id].items(), key=operator.itemgetter(1))]
                        layout = go.Layout(
                            xaxis=dict(
                                type = 'category',
                                tickvals = list(range(len(ticks))),
                                ticktext = ticks,
                                title = attribute_name
                            ),
                        )
                        figure = go.Figure(data=data, layout=layout)
                    else:
                        figure = go.Figure(data=data)
                    filename =  'visuals/1D_Count'+'_'+str(os.getpid())+'.html'
                    plotly.offline.plot(figure, filename=filename, auto_open = False)
                    print(filename)
                elif (len(dimensions) == 2 and 1 not in dimensions) or len(dimensions) == 3 and 1 in dimensions:
                    y = dimensions[1]
                    sublists = [histogram[i:i+y] for i in xrange(0, len(histogram), y)]
                    trace = go.Heatmap(z=sublists)
                    data = [trace]
                    # print(sublists)
                    if len(configuration['attributes']) == 2:
                        attribute_ids = configuration['attributes']
                        attribute_names = [mesh_dict_inverted[attribute_id] for attribute_id in attribute_ids]
                        x_ticks = [str(mesh_dict_inverted[k]) for k in possible_values[0]]
                        y_ticks = [str(mesh_dict_inverted[k]) for k in possible_values[1]]
                        layout = go.Layout(
                            xaxis=dict(
                                type = 'category',
                                tickvals = list(range(len(y_ticks))),
                                ticktext = y_ticks,
                                title = attribute_names[0]
                            ),
                            yaxis=dict(
                                type = 'category',
                                tickangle = -45,
                                tickvals = list(range(len(x_ticks))),
                                ticktext = x_ticks,
                                title = attribute_names[1]
                            )
                        )
                        figure = go.Figure(data=data, layout=layout)
                    else:
                        figure = go.Figure(data=data)
                    filename =  'visuals/2D_Count'+'_'+str(os.getpid())+'.html'
                    plotly.offline.plot(figure, filename=filename, auto_open = False)
                    print(filename)

                break


if __name__ == '__main__':
    main()