import sys
import json

OUTFILE = sys.argv[1]

response = []
with open(OUTFILE) as results:
    ai = 1
    for line in results:
        if line.startswith('{') and 'Histogram' in line:
            dimensions = [int(x) for x in (line[1:-(len('Histogram')+3)]).split(', ')]
            histogram = [int(x) for x in (next(results)[1:-2]).split(', ')]
            res = {'cellsPerDimension' : dimensions, 'histogram' : histogram}
            response.append(res)
json_data = json.dumps(response)
print(json_data)