import os
import sys
import plotly
import plotly.graph_objs as go
import json
import pandas as pd

configuration = json.load(open('configuration.json'))

mins = []
maxs = []


if len(sys.argv) > 1:
    DATASET = sys.argv[1]
else:
    DATASET = 'syndata_upload_and_scaling_tests/centricity_identified_filtered_edited.csv'

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

with open('data_input.sc', 'r') as data_input: # Temporary solution
    line = next(data_input)
    while not line.startswith('pd_shared3p float64[[1]] imported_mins'):
        line = next(data_input)
    mins = map(float,line.split()[-1][1:-2].split(','))
    line = next(data_input)
    maxs = map(float,line.split()[-1][1:-2].split(','))
    df = pd.read_csv(DATASET,sep=',')


with open('out.txt', 'r') as results:
    ai = 1
    for line in results:
        if line.startswith('{') and 'Histogram' in line:
            dimensions = [int(x) for x in (line[1:-(len('Histogram')+3)]).split(', ')]
            histogram = [int(x) for x in (next(results)[1:-2]).split(', ')]
            x = dimensions[0]
            if len(dimensions) == 1 or (len(dimensions) == 2 and 1 in dimensions):
                data = [go.Bar(y=histogram)]
                if not isinstance(configuration['attributes'], list):
                    attribute_index = df.columns.get_loc(configuration['attributes'])
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
                            title = configuration['attributes']
                        ),
                    )
                    figure = go.Figure(data=data, layout=layout)
                else:
                    figure = go.Figure(data=data)
                filename =  'web/visuals/1D_Histogram'+'_'+str(os.getpid())+'_'+str(ai)+'.html'
                plotly.offline.plot(figure, filename=filename, auto_open = False)
                print('/'.join(filename.split('/')[2:]))
            elif len(dimensions) == 2 and 1 not in dimensions:
                y = dimensions[1]
                sublists = [histogram[i:i+y] for i in xrange(0, len(histogram), y)]
                trace = go.Heatmap(z=sublists)
                data = [trace]
                if isinstance(configuration['attributes'], list) and len(configuration['attributes']) == 2:
                    attribute_indexes = [df.columns.get_loc(attribute) for attribute in configuration['attributes'] ]
                    attribute_mins = [mins[i] for i in attribute_indexes]
                    attribute_maxs = [maxs[i] for i in attribute_indexes]
                    cell_widths = [(attribute_maxs[i] - attribute_mins[i]) / dimensions[i] for i in range(len(dimensions))]
                    layout = go.Layout(
                        xaxis=dict(
                            type = 'category',
                            tickvals = list(range(dimensions[1])),
                            ticktext = compute_axis_labels(attribute_mins[1], attribute_maxs[1], cell_widths[1], dimensions[1]),
                            title = configuration['attributes'][1]
                        ),
                        yaxis=dict(
                            type = 'category',
                            tickangle = -45,
                            tickvals = list(range(dimensions[0])),
                            ticktext = compute_axis_labels(attribute_mins[0], attribute_maxs[0], cell_widths[0], dimensions[0]),
                            title = configuration['attributes'][0]
                        )
                    )
                    figure = go.Figure(data=data, layout=layout)
                else:
                    figure = go.Figure(data=data)
                filename = 'web/visuals/2D_Histogram'+'_'+str(os.getpid())+'_'+str(ai)+'.html'
                plotly.offline.plot(figure, filename=filename, auto_open = False)
                print('/'.join(filename.split('/')[2:]))
            ai += 1

