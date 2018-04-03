import plotly
import plotly.graph_objs as go
import json

configuration = json.load(open('configuration.json'))

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
                    layout = go.Layout(
                        xaxis=dict(
                            type = 'category',
                            title = configuration['attributes']
                        ),
                    )
                    figure = go.Figure(data=data, layout=layout)
                else:
                    figure = go.Figure(data=data)
                plotly.offline.plot(figure, filename='visuals/1D_Histogram'+str(ai))
            elif len(dimensions) == 2 and 1 not in dimensions:
                y = dimensions[1]
                sublists = [histogram[i:i+y] for i in xrange(0, len(histogram), y)]
                print(sublists)
                trace = go.Heatmap(z=sublists)
                data = [trace]
                if isinstance(configuration['attributes'], list) and len(configuration['attributes']) == 2:
                    layout = go.Layout(
                        xaxis=dict(
                            type = 'category',
                            title = configuration['attributes'][1]
                        ),
                        yaxis=dict(
                            type = 'category',
                            title = configuration['attributes'][0]
                        )
                    )
                    figure = go.Figure(data=data, layout=layout)
                else:
                    figure = go.Figure(data=data)
                plotly.offline.plot(figure, filename='visuals/2D_Histogram'+str(ai))
            ai += 1

