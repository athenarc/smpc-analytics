import os
import sys
import plotly
import plotly.graph_objs as go
import json
import argparse
import pandas as pd
import numpy as np


mins = []
maxs = []


parser = argparse.ArgumentParser()
parser.add_argument('configuration', help = 'Configuration file of the request')
parser.add_argument('--columns', help = 'CSV File with the columns of the global schema.', default = '../datasets/analysis_test_data/columns.csv')
parser.add_argument('--summary', help = 'CSV file with the summary of the dataset.', default = '../datasets/analysis_test_data/cvi_summary.csv')
args = parser.parse_args()

def compute_axis_labels(min, max, width, cells):
    start = min
    ticks = []
    for c in range(cells-1):
        end = start + width
        ticks.append('['+"{0:.2f}".format(start)+', '+"{0:.2f}".format(end)+')')
        start = end
    end = start + width
    ticks.append('['+"{0:.2f}".format(start)+', '+"{0:.2f}".format(end)+']')
    return ticks

uid = args.configuration.split('_')[-1].split('.')[0]
configuration = json.load(open(args.configuration))

df = pd.read_csv(args.columns,sep=',')
mins = []
maxs = []
summary = pd.read_csv(args.summary, sep = ',')
for attribute in df.columns:
    if attribute in summary['Field'].values:
        mins.append(summary[summary['Field']==attribute][' Min'].item())
        maxs.append(summary[summary['Field']==attribute][' Max'].item())
    else:
        mins.append(0.0)
        maxs.append(0.0)

with open('../out_' + uid + '.txt', 'r') as results:
    ai = 1
    for line in results:
        if line.startswith('{') and 'Histogram' in line:
            dimensions = [int(x) for x in (line[1:-(len('Histogram')+3)]).split(', ')]
            histogram = [int(x) for x in (next(results)[1:-2]).split(', ')]
            x = dimensions[0]
            if len(dimensions) == 1 or (len(dimensions) == 2 and 1 in dimensions):
                data = [go.Bar(y=histogram)]
                if len(configuration['attributes'][0]) == 1:
                    attribute_name = configuration['attributes'][0][0]['name']
                    attribute_index = df.columns.get_loc(attribute_name)
                    attribute_min = mins[attribute_index]
                    attribute_max = maxs[attribute_index]
                    cells = x
                    cell_width = (attribute_max - attribute_min) / cells
                    start = attribute_min
                    layout = go.Layout(
                        xaxis=dict(
                            type = 'category',
                            tickvals = list(range(cells)),
                            ticktext = compute_axis_labels(attribute_min, attribute_max, cell_width, cells),
                            title = attribute_name
                        ),
                    )
                    figure = go.Figure(data=data, layout=layout)
                else:
                    figure = go.Figure(data=data)
                filename =  'visuals/1D_Histogram'+'_'+str(os.getpid())+'_'+str(ai)+'.html'
                plotly.offline.plot(figure, filename=filename, auto_open = False)
                print(filename)
            elif (len(dimensions) == 2 and 1 not in dimensions) or len(dimensions) == 3 and 1 in dimensions:
                y = dimensions[1]
                sublists = [histogram[i:i+y] for i in xrange(0, len(histogram), y)]
                trace = go.Heatmap(z=sublists)
                data = [trace]
                if len(configuration['attributes'][0]) == 2:
                    attribute_names = [x['name'] for x in configuration['attributes'][0]]
                    attribute_indexes = [df.columns.get_loc(attribute) for attribute in attribute_names ]
                    attribute_mins = [mins[i] for i in attribute_indexes]
                    attribute_maxs = [maxs[i] for i in attribute_indexes]
                    cell_widths = [(attribute_maxs[i] - attribute_mins[i]) / dimensions[i] for i in range(len(dimensions))]
                    layout = go.Layout(
                        xaxis=dict(
                            type = 'category',
                            tickvals = list(range(dimensions[1])),
                            ticktext = compute_axis_labels(attribute_mins[1], attribute_maxs[1], cell_widths[1], dimensions[1]),
                            title = attribute_names[1]
                        ),
                        yaxis=dict(
                            type = 'category',
                            tickangle = -45,
                            tickvals = list(range(dimensions[0])),
                            ticktext = compute_axis_labels(attribute_mins[0], attribute_maxs[0], cell_widths[0], dimensions[0]),
                            title = attribute_names[0]
                        )
                    )
                    figure = go.Figure(data=data, layout=layout)
                else:
                    figure = go.Figure(data=data)
                filename = 'visuals/2D_Histogram'+'_'+str(os.getpid())+'_'+str(ai)+'.html'
                plotly.offline.plot(figure, filename=filename, auto_open = False)
                print(filename)
            elif len(dimensions) == 3 and 1 not in dimensions:
                y = dimensions[1]
                z = dimensions[2]
                data = []
                sublists = [histogram[i:i+x*y] for i in xrange(0, len(histogram), x*y)]

                for i in range(z):
                    array = [i]*(x*y)
                    array = [array[i:i+x] for j in xrange(0, len(array), x)]
                    colors = sublists[i]
                    colors = [colors[i:i+x] for j in xrange(0, len(colors), x)]
                    text = [map(str,j) for j in colors]
                    data.append(go.Surface(z = array,
                                            surfacecolor = colors,
                                            text = text,
                                            colorscale = [[0, 'rgb('+ ','.join(map(str,list(np.random.choice(range(256), size=3)))) +')'], [1, 'rgb('+ ','.join(map(str,list(np.random.choice(range(256), size=3)))) +')']],
                                            colorbar = dict(
                                                x = 1+0.05*i
                                                )
                                            ))
                if len(configuration['attributes'][0]) == 3:
                    attribute_names = [x['name'] for x in configuration['attributes'][0]]
                    attribute_indexes = [df.columns.get_loc(attribute) for attribute in attribute_names ]
                    attribute_mins = [mins[i] for i in attribute_indexes]
                    attribute_maxs = [maxs[i] for i in attribute_indexes]
                    cell_widths = [(attribute_maxs[i] - attribute_mins[i]) / dimensions[i] for i in range(len(dimensions))]
                    layout = go.Layout(
                        scene = dict(
                            zaxis=dict(
                                # type = 'category',
                                tickvals = list(range(dimensions[2])),
                                ticktext = compute_axis_labels(attribute_mins[2], attribute_maxs[2], cell_widths[2], dimensions[2]),
                                title = attribute_names[2]
                            ),
                            yaxis=dict(
                                # type = 'category',
                                tickangle = -45,
                                tickvals = list(range(dimensions[1])),
                                ticktext = compute_axis_labels(attribute_mins[1], attribute_maxs[1], cell_widths[1], dimensions[1]),
                                title = attribute_names[1]
                            ),
                            xaxis=dict(
                                # type = 'category',
                                tickangle = -45,
                                tickvals = list(range(dimensions[0])),
                                ticktext = compute_axis_labels(attribute_mins[0], attribute_maxs[0], cell_widths[0], dimensions[0]),
                                title = attribute_names[0]
                            )
                        )
                    )
                    figure = go.Figure(data=data, layout=layout)
                else:
                    figure = go.Figure(data=data)
                filename = 'visuals/3D_Histogram'+'_'+str(os.getpid())+'_'+str(ai)+'.html'
                plotly.offline.plot(figure, filename=filename, auto_open = False)
                print(filename)
            ai += 1

