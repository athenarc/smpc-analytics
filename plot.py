import plotly
import plotly.graph_objs as go

with open('out.txt', 'r') as results:
    ai = 0
    for line in results:
        if line.startswith('{') and 'Histogram' in line:
            dimensions = [int(x) for x in (line[1:-(len('Histogram')+3)]).split(', ')]
            histogram = [int(x) for x in (next(results)[1:-2]).split(', ')]
            if len(dimensions) == 2 and 1 not in dimensions:
                x = dimensions[0]
                y = dimensions[1]
                sublists = [histogram[i:i+y] for i in xrange(0, len(histogram), y)]
                trace = go.Heatmap(z=sublists)
                data=[trace]
                plotly.offline.plot(data, filename='labelled-heatmap'+str(ai))
                ai += 1
