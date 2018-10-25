import math
import time
import sys
import cProfile
# from random_example_generator import examples

original_attributes = ['petal length', 'petal width', 'sepal width', 'sepal length', 'flower']

examples = [[4.3, 3.0, 1.1, 0.1, 'Iris-setosa'],
 [4.8, 3.0, 1.4, 0.1, 'Iris-setosa'],
 [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
 [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
 [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
 [5.2, 4.1, 1.5, 0.1, 'Iris-setosa'],
 [4.6, 3.6, 1.0, 0., 'Iris-setosa'],
 [5.0, 3.2, 1.2, 0.2, 'Iris-setosa'],
 [5.8, 4.0, 1.2, 0.2, 'Iris-setosa'],
 [4.4, 3.0, 1.3, 0.2, 'Iris-setosa'],
 [4.4, 3.2, 1.3, 0.2, 'Iris-setosa'],
 [4.7, 3.2, 1.3, 0.2, 'Iris-setosa'],
 [5.5, 3.5, 1.3, 0.2, 'Iris-setosa'],
 [4.4, 2.9, 1.4, 0.2, 'Iris-setosa'],
 [4.9, 3.0, 1.4, 0.2, 'Iris-setosa'],
 [4.6, 3.2, 1.4, 0.2, 'Iris-setosa'],
 [5.0, 3.3, 1.4, 0.2, 'Iris-setosa'],
 [5.2, 3.4, 1.4, 0.2, 'Iris-setosa'],
 [5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
 [5.0, 3.6, 1.4, 0.2, 'Iris-setosa'],
 [5.5, 4.2, 1.4, 0.2, 'Iris-setosa'],
 [4.6, 3.1, 1.5, 0.2, 'Iris-setosa'],
 [5.0, 3.4, 1.5, 0.2, 'Iris-setosa'],
 [5.1, 3.4, 1.5, 0.2, 'Iris-setosa'],
 [5.2, 3.5, 1.5, 0.2, 'Iris-setosa'],
 [5.3, 3.7, 1.5, 0.2, 'Iris-setosa'],
 [5.4, 3.7, 1.5, 0.2, 'Iris-setosa'],
 [5.0, 3.0, 1.6, 0.2, 'Iris-setosa'],
 [4.8, 3.1, 1.6, 0.2, 'Iris-setosa'],
 [4.7, 3.2, 1.6, 0.2, 'Iris-setosa'],
 [4.8, 3.4, 1.6, 0.2, 'Iris-setosa'],
 [5.1, 3.8, 1.6, 0.2, 'Iris-setosa'],
 [5.4, 3.4, 1.7, 0.2, 'Iris-setosa'],
 [4.8, 3.4, 1.9, 0.2, 'Iris-setosa'],
 [4.5, 2.3, 1.3, 0.3, 'Iris-setosa'],
 [5.0, 3.5, 1.3, 0.3, 'Iris-setosa'],
 [4.8, 3.0, 1.4, 0.3, 'Iris-setosa'],
 [4.6, 3.4, 1.4, 0.3, 'Iris-setosa'],
 [5.1, 3.5, 1.4, 0.3, 'Iris-setosa'],
 [5.1, 3.8, 1.5, 0.3, 'Iris-setosa'],
 [5.7, 3.8, 1.7, 0.3, 'Iris-setosa'],
 [5.4, 3.9, 1.3, 0.4, 'Iris-setosa'],
 [5.4, 3.4, 1.5, 0.4, 'Iris-setosa'],
 [5.1, 3.7, 1.5, 0.4, 'Iris-setosa'],
 [5.7, 4.4, 1.5, 0.4, 'Iris-setosa'],
 [5.0, 3.4, 1.6, 0.4, 'Iris-setosa'],
 [5.4, 3.9, 1.7, 0.4, 'Iris-setosa'],
 [5.1, 3.8, 1.9, 0.4, 'Iris-setosa'],
 [5.1, 3.3, 1.7, 0.5, 'Iris-setosa'],
 [5.0, 3.5, 1.6, 0.6, 'Iris-setosa'],
 [5.0, 2.3, 3.3, 1.0, 'Iris-versicolor'],
 [4.9, 2.4, 3.3, 1.0, 'Iris-versicolor'],
 [5.0, 2.0, 3.5, 1.0, 'Iris-versicolor'],
 [5.7, 2.6, 3.5, 1.0, 'Iris-versicolor'],
 [5.5, 2.4, 3.7, 1.0, 'Iris-versicolor'],
 [6.0, 2.2, 4.0, 1.0, 'Iris-versicolor'],
 [5.8, 2.7, 4.1, 1.0, 'Iris-versicolor'],
 [5.1, 2.5, 3.0, 1.1, 'Iris-versicolor'],
 [5.5, 2.4, 3.8, 1.1, 'Iris-versicolor'],
 [5.6, 2.5, 3.9, 1.1, 'Iris-versicolor'],
 [5.8, 2.7, 3.9, 1.2, 'Iris-versicolor'],
 [5.8, 2.6, 4.0, 1.2, 'Iris-versicolor'],
 [5.7, 3.0, 4.2, 1.2, 'Iris-versicolor'],
 [5.5, 2.6, 4.4, 1.2, 'Iris-versicolor'],
 [6.1, 2.8, 4.7, 1.2, 'Iris-versicolor'],
 [5.6, 2.9, 3.6, 1.3, 'Iris-versicolor'],
 [5.5, 2.3, 4.0, 1.3, 'Iris-versicolor'],
 [5.5, 2.5, 4.0, 1.3, 'Iris-versicolor'],
 [6.1, 2.8, 4.0, 1.3, 'Iris-versicolor'],
 [5.7, 2.8, 4.1, 1.3, 'Iris-versicolor'],
 [5.6, 3.0, 4.1, 1.3, 'Iris-versicolor'],
 [5.6, 2.7, 4.2, 1.3, 'Iris-versicolor'],
 [5.7, 2.9, 4.2, 1.3, 'Iris-versicolor'],
 [6.2, 2.9, 4.3, 1.3, 'Iris-versicolor'],
 [6.4, 2.9, 4.3, 1.3, 'Iris-versicolor'],
 [6.3, 2.3, 4.4, 1.3, 'Iris-versicolor'],
 [5.7, 2.8, 4.5, 1.3, 'Iris-versicolor'],
 [6.6, 2.9, 4.6, 1.3, 'Iris-versicolor'],
 [5.2, 2.7, 3.9, 1.4, 'Iris-versicolor'],
 [6.6, 3.0, 4.4, 1.4, 'Iris-versicolor'],
 [6.7, 3.1, 4.4, 1.4, 'Iris-versicolor'],
 [6.1, 3.0, 4.6, 1.4, 'Iris-versicolor'],
 [6.1, 2.9, 4.7, 1.4, 'Iris-versicolor'],
 [7.0, 3.2, 4.7, 1.4, 'Iris-versicolor'],
 [6.8, 2.8, 4.8, 1.4, 'Iris-versicolor'],
 [6.1, 2.6, 5.6, 1.4, 'Iris-virginica'],
 [5.9, 3.0, 4.2, 1.5, 'Iris-versicolor'],
 [6.2, 2.2, 4.5, 1.5, 'Iris-versicolor'],
 [6.0, 2.9, 4.5, 1.5, 'Iris-versicolor'],
 [5.4, 3.0, 4.5, 1.5, 'Iris-versicolor'],
 [5.6, 3.0, 4.5, 1.5, 'Iris-versicolor'],
 [6.4, 3.2, 4.5, 1.5, 'Iris-versicolor'],
 [6.5, 2.8, 4.6, 1.5, 'Iris-versicolor'],
 [6.7, 3.1, 4.7, 1.5, 'Iris-versicolor'],
 [6.3, 2.5, 4.9, 1.5, 'Iris-versicolor'],
 [6.9, 3.1, 4.9, 1.5, 'Iris-versicolor'],
 [6.0, 2.2, 5.0, 1.5, 'Iris-virginica'],
 [6.3, 2.8, 5.1, 1.5, 'Iris-virginica'],
 [6.0, 3.4, 4.5, 1.6, 'Iris-versicolor'],
 [6.3, 3.3, 4.7, 1.6, 'Iris-versicolor'],
 [6.0, 2.7, 5.1, 1.6, 'Iris-versicolor'],
 [7.2, 3.0, 5.8, 1.6, 'Iris-virginica'],
 [4.9, 2.5, 4.5, 1.7, 'Iris-virginica'],
 [6.7, 3.0, 5.0, 1.7, 'Iris-versicolor'],
 [6.2, 2.8, 4.8, 1.8, 'Iris-virginica'],
 [6.0, 3.0, 4.8, 1.8, 'Iris-virginica'],
 [5.9, 3.2, 4.8, 1.8, 'Iris-versicolor'],
 [6.3, 2.7, 4.9, 1.8, 'Iris-virginica'],
 [6.1, 3.0, 4.9, 1.8, 'Iris-virginica'],
 [5.9, 3.0, 5.1, 1.8, 'Iris-virginica'],
 [6.5, 3.0, 5.5, 1.8, 'Iris-virginica'],
 [6.4, 3.1, 5.5, 1.8, 'Iris-virginica'],
 [6.3, 2.9, 5.6, 1.8, 'Iris-virginica'],
 [6.7, 2.5, 5.8, 1.8, 'Iris-virginica'],
 [7.2, 3.2, 6.0, 1.8, 'Iris-virginica'],
 [7.3, 2.9, 6.3, 1.8, 'Iris-virginica'],
 [6.3, 2.5, 5.0, 1.9, 'Iris-virginica'],
 [5.8, 2.7, 5.1, 1.9, 'Iris-virginica'],
 [5.8, 2.7, 5.1, 1.9, 'Iris-virginica'],
 [6.4, 2.7, 5.3, 1.9, 'Iris-virginica'],
 [7.4, 2.8, 6.1, 1.9, 'Iris-virginica'],
 [5.6, 2.8, 4.9, 2.0, 'Iris-virginica'],
 [5.7, 2.5, 5.0, 2.0, 'Iris-virginica'],
 [6.5, 3.2, 5.1, 2.0, 'Iris-virginica'],
 [6.5, 3.0, 5.2, 2.0, 'Iris-virginica'],
 [7.9, 3.8, 6.4, 2.0, 'Iris-virginica'],
 [7.7, 2.8, 6.7, 2.0, 'Iris-virginica'],
 [6.9, 3.1, 5.4, 2.1, 'Iris-virginica'],
 [6.8, 3.0, 5.5, 2.1, 'Iris-virginica'],
 [6.4, 2.8, 5.6, 2.1, 'Iris-virginica'],
 [6.7, 3.3, 5.7, 2.1, 'Iris-virginica'],
 [7.1, 3.0, 5.9, 2.1, 'Iris-virginica'],
 [7.6, 3.0, 6.6, 2.1, 'Iris-virginica'],
 [6.4, 2.8, 5.6, 2.2, 'Iris-virginica'],
 [6.5, 3.0, 5.8, 2.2, 'Iris-virginica'],
 [7.7, 3.8, 6.7, 2.2, 'Iris-virginica'],
 [6.9, 3.1, 5.1, 2.3, 'Iris-virginica'],
 [6.7, 3.0, 5.2, 2.3, 'Iris-virginica'],
 [6.4, 3.2, 5.3, 2.3, 'Iris-virginica'],
 [6.2, 3.4, 5.4, 2.3, 'Iris-virginica'],
 [6.9, 3.2, 5.7, 2.3, 'Iris-virginica'],
 [6.8, 3.2, 5.9, 2.3, 'Iris-virginica'],
 [7.7, 3.0, 6.1, 2.3, 'Iris-virginica'],
 [7.7, 2.6, 6.9, 2.3, 'Iris-virginica'],
 [5.8, 2.8, 5.1, 2.4, 'Iris-virginica'],
 [6.7, 3.1, 5.6, 2.4, 'Iris-virginica'],
 [6.3, 3.4, 5.6, 2.4, 'Iris-virginica'],
 [6.7, 3.3, 5.7, 2.5, 'Iris-virginica'],
 [6.3, 3.3, 6.0, 2.5, 'Iris-virginica'],
 [7.2, 3.6, 6.1, 2.5, 'Iris-virginica']]

possible_values = {'sepal length': 'continuous',
'sepal width': 'continuous',
'petal length': 'continuous',
'petal width': 'continuous',
'flower' : ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']}

categorical_attributes = ['flower']

class_attribute = 'flower'

CELL_COUNT = 5
mins = [min([example[original_attributes.index(attribute)] for example in examples]) if attribute not in categorical_attributes else 0 for attribute in original_attributes]
maxs = [max([example[original_attributes.index(attribute)] for example in examples]) if attribute not in categorical_attributes else 0 for attribute in original_attributes]
cells = [CELL_COUNT if attribute not in categorical_attributes else len(possible_values[attribute]) for attribute in original_attributes]

path = {'attributes' : [], 'operators' : [], 'values' : []}

def histogram(examples, attributes, cells, mins, maxs):
    positions = [0] * len(examples)
    requested_attributes = len(attributes)
    for a in range(requested_attributes):
        attribute = attributes[a]
        attribute_index = original_attributes.index(attribute)
        number_of_cells = cells[a]
        if attribute not in categorical_attributes:
            max = maxs[attribute_index]
            min = mins[attribute_index]
            width = float(max - min) / number_of_cells
            cellmap = [int(float(example[attribute_index] - min) / width) for example in examples]
            cellmap = [c - int(c == number_of_cells) for c in cellmap]
        else:
            cellmap = [possible_values[attribute].index(example[attribute_index]) for example in examples]
        prod = product(cells[a+1:])
        positions = [pos + c * prod for pos,c in zip(positions, cellmap)]
    length = product(cells)
    histogram = [0] * length
    for j in range(length):
        eq = [p == j for p in positions]
        histogram[j] = sum(eq)
    return histogram

def product(lst):
    p = 1
    for e in lst:
        p = p * e
    return p


def all_examples_same(path):
    same = 0
    total_count = get_count(path)
    label = ''
    for value in possible_values[class_attribute]: # [Yes, No]
        attributes = path['attributes']
        operators = path['operators']
        values = path['values']
        count = get_count({'attributes' : attributes + [class_attribute], 'operators' : operators + ['='], 'values' : values + [value]})
        same += int(count == total_count)
        label = value if count == total_count else ''
    return (same == 1), label 

def split_attribute(path, attributes):
    # print("Examples are ",examples);
    splitted = []
    max_gain = -1 * float('inf')
    best_threshold = -1
    best_attribute = -1
    best_splitted = -1
    path_attributes = path['attributes']
    path_operators = path['operators']
    path_values = path['values']
    
    ent = entropy(path)
    count = get_count(path)
    
    for attribute in attributes:
        attribute_index = attribute_index = original_attributes.index(attribute)
        if attribute in categorical_attributes:
            splitted = []
            for value in possible_values[attribute]:
                subset = {'attributes' : path_attributes+[attribute], 'operators' : path_operators+['='], 'values' : path_values + [value]}# subset of examples that have attribute = value
                splitted.append(subset)
                
            gain = information_gain(ent, count, splitted)
            if gain > max_gain:
                max_gain = gain
                best_attribute = attribute
                best_splitted = splitted
        else:
            number_of_cells = cells[attribute_index]
            for threshold in range(number_of_cells):
                
                splitted = [{'attributes' : path_attributes+[attribute], 'operators' : path_operators+['<='], 'values' : path_values + [threshold]}, {'attributes' : path_attributes+[attribute], 'operators' : path_operators+['>'], 'values' : path_values + [threshold]}]
                gain = information_gain(ent, count, splitted)
                # print("GAIN ", gain)
                # print("GAIN ", max_gain)
                if gain > max_gain:
                    max_gain = gain
                    best_attribute = attribute
                    best_threshold = threshold
                    best_splitted = splitted
    return best_attribute, best_threshold, best_splitted


def most_common_label(path):
    label_counts = {}
    for value in possible_values[class_attribute]: # [Yes, No]
        attributes = path['attributes']
        operators = path['operators']
        values = path['values']
        count = get_count({'attributes' : attributes + [class_attribute], 'operators' : operators + ['='], 'values' : values + [value]})
        label_counts[value] = count
    return( max(label_counts, key=label_counts.get))

def entropy(path):
    entropy = 0.0
    total_count = get_count(path)
    for value in possible_values[class_attribute]: # [Yes, No]
        # count = sum([1 for example in examples if example[-1] == value]) # count occurencies of value in examples
        attributes = path['attributes']
        operators = path['operators']
        values = path['values']
        count = get_count({'attributes' : attributes + [class_attribute], 'operators' : operators + ['='], 'values' : values + [value]})
        percentage = float(count) / total_count
        if percentage != 0:
            entropy -= (percentage * math.log(percentage, 2))
    return entropy

def get_count(path):
    # print(path)
    attributes = path['attributes']
    operators = path['operators']
    values = path['values']
    attribute_indexes = [original_attributes.index(attribute) for attribute in attributes]
    total_count = 1
    
    # print("attributes: ",attributes)
    dimensions = []
    for original_attribute in original_attributes:
        if original_attribute in attributes:
            attribute = original_attribute
            i = attributes.index(attribute)
            attribute_index = attribute_indexes[i]
            operator = operators[i]
            value = values[i]
            if operator == '<=':
                total_count *= (value + 1)
                dimensions.append(value + 1)
            elif operator == '>':
                difference = cells[attribute_index] - (value + 1)
                # print('difference:' + str(difference))
                if difference != 0:
                    total_count *= difference
                    dimensions.append(difference)
                else:
                    # print('Count for' + str(path)+' is 0')
                    return 0
            else:
                dimensions.append(1)
        else:
            original_index = original_attributes.index(original_attribute)
            total_count *= cells[original_index]
            dimensions.append(cells[original_index])
        # print(original_attribute, dimensions)
    # print('Total count: '+str(total_count))
    # print(dimensions)
    
    constraints = [[-1] * len(original_attributes) for i in range(total_count)]
    for original_attribute in original_attributes:
        if original_attribute in attributes:
            attribute = original_attribute
            i = attributes.index(attribute)
            attribute_index = attribute_indexes[i]
            operator = operators[i]
            value = values[i]
            if operator == '=':
                for constraint in constraints:
                    constraint[attribute_index] = possible_values[attribute].index(value)
            elif operator == '<=':
                less_list = range(value + 1)
                for j in range(len(constraints)):
                    constraint = constraints[j]
                    constraint[attribute_index] = less_list[j % len(less_list)]
            else:
                greater_list = range(value + 1, cells[attribute_index])
                # print(greater_list, value)
                for j in range(len(constraints)):
                    constraint = constraints[j]
                    constraint[attribute_index] = greater_list[j % len(greater_list)]
        else:
            for j in range(len(constraints)):
                constraint = constraints[j]
                original_index = original_attributes.index(original_attribute)
                prod = product(dimensions[original_index + 1:])
                constraint[original_index] = (j / prod) % dimensions[original_index] 
                
    count = 0
    for constraint in constraints:
        # print("constraint: ", constraint)
        index = get_single_index(constraint)
        count += hist[index]
        # print('hist['+str(index)+'] = '+str(hist[index]))
    # print('Count for' + str(path)+' is '+str(count))
    return count


def get_single_index(index_list):
    position = 0
    for dimension in range(len(index_list)):
        index = index_list[dimension]
        prod = product(cells[dimension+1:])
        position += index * prod
    return position


def information_gain(gain, length, subsets):
    for subset in subsets:
        percentage = float(get_count(subset)) / length
        if percentage != 0:
            gain -= (percentage*entropy(subset))
    return gain


ENTROPY_THRESHOLD = 0.5

def c45(path, attributes):
    all_same, label = all_examples_same(path)
    if all_same:
        return label
    ent = entropy(path)
    # print(ent, " for path ", path)
    if ent < ENTROPY_THRESHOLD:
        return str(most_common_label(path))
    # if len(attributes) == 0:
    #     return str(most_common_label(path))
    best_attribute, best_threshold, splitted = split_attribute(path, attributes) #find best attribute
    best_attribute_original_index = original_attributes.index(best_attribute)
    # best_attribute_index = attributes.index(best_attribute)
    branches = []
    if best_attribute in categorical_attributes:
        for i in range(len(possible_values[best_attribute])):
            value = possible_values[best_attribute][i]
            branch = '"' + str(best_attribute)+' == '+str(value) + '"'
            subset = splitted[i]
            
            if get_count(subset) == 0: 
                branch += ' : ' + str(most_common_label(path))
            else:
                # branch  += ' : ' + str(c45(subset, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
                branch  += ' : ' + str(c45(subset, attributes))
            branches.append(branch)
    else:
        branch = '"' + str(best_attribute)+' <= '+str(best_threshold) + '"'
        less = splitted[0]
        if get_count(less) == 0:
            branch += ' : ' + str(most_common_label(path))
        else:
            # branch  += ' : ' + str(c45(less, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
            branch  += ' : ' + str(c45(less, attributes))

        branches.append(branch)
        branch = '"' + str(best_attribute)+' > '+str(best_threshold) + '"'
        greater = splitted[1]
        if get_count(greater) == 0:
            branch += ' : ' + str(most_common_label(path))
        else:
            # branch  += ' : ' + str(c45(greater, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
            branch  += ' : ' + str(c45(greater, attributes))
        branches.append(branch)
    root = '{ '+ ', '.join(branches) +' }'
    return root


histogram_time = time.time()
hist = histogram(examples, original_attributes, cells, mins, maxs)
print('Histogram time: '+ str(time.time()-histogram_time))
c45_time = time.time()
# cProfile.run('c45(path,original_attributes[:-1])')
print(c45(path,original_attributes[:-1]))
print('C4.5 time: '+ str(time.time()-c45_time))
print('Total time: '+ str(time.time()-histogram_time))
print('Histogram size: ' + str(len(hist)))
print(str(len(examples)) + ' patients')

