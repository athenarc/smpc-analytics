# Usage: from random_example_generator import examples
import random

NUM = 1000
mins = [4.3, 2.0, 1.0, 0.1]
maxs = [7.9, 4.4, 6.9, 2.5]
classes = ['Iris-versicolor', 'Iris-virginica', 'Iris-setosa']

random.seed(0)

examples = []
for i in range(NUM):
    examples.append([random.uniform(mins[j], maxs[j]) for j in range(len(mins))] + [classes[random.randint(0,len(classes)-1)]])
