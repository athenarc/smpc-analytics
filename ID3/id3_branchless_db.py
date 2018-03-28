import math

original_attributes = [0,1,2,3,4]

# examples = [['Sunny','Hot','High','Weak','No'],
#             ['Sunny','Hot','High','Strong','No'],
#             ['Overcast','Hot','High','Weak','Yes'],
#             ['Rain','Mild','High','Weak','Yes'],
#             ['Rain','Cool','Normal','Weak','Yes'],
#             ['Rain','Cool','Normal','Strong','No'],
#             ['Overcast','Cool','Normal','Strong','Yes'],
#             ['Sunny','Mild','High','Weak','No'],
#             ['Sunny','Cool','Normal','Weak','Yes'],
#             ['Rain','Mild','Normal','Weak','Yes'],
#             ['Sunny','Mild','Normal','Strong','Yes'],
#             ['Overcast','Mild','High','Strong','Yes'],
#             ['Overcast','Hot','Normal','Weak','Yes'],
#             ['Rain','Mild','High','Strong','No']]
#
# possible_values = {'Outlook':['Sunny', 'Overcast', 'Rain'],
#                     'Temperature':['Hot', 'Mild', 'Cool'],
#                     'Humidity':['Normal', 'High'],
#                     'Wind':['Weak', 'Strong'],
#                     'Play ball?':['Yes', 'No']}

original_examples = [[0,0,1,0,1],
                    [0,0,1,1,1],
                    [1,0,1,0,0],
                    [2,1,1,0,0],
                    [2,2,0,0,0],
                    [2,2,0,1,1],
                    [1,2,0,1,0],
                    [0,1,1,0,1],
                    [0,2,0,0,0],
                    [2,1,0,0,0],
                    [0,1,0,1,0],
                    [1,1,1,1,0],
                    [1,0,0,0,0],
                    [2,1,1,1,1]]

possible_values = {0:[0, 1, 2],
                    1:[0, 1, 2],
                    2:[0, 1, -1],
                    3:[0, 1, -1],
                    4:[0, 1, -1]}
class_attribute = 4


def all_examples_same(example_indexes):
    res = 0
    class_counts = [0]*len(possible_values[class_attribute])
    label_column = [row[class_attribute] for row in original_examples]
    for i in range(len(possible_values[class_attribute])):
        neq = int(i != -1)
        for index in range(len(example_indexes)):
            class_counts[i] += int(label_column[index] == i) * neq * (example_indexes[index] != 0)
        res += int(class_counts[i] == sum(example_indexes))
    return res

def best(example_indexes, attributes):
    max_gain = information_gain(example_indexes, attributes[0])
    best = attributes[0]
    for i in range(1, len(attributes)):
        a = attributes[i]
        gain = information_gain(example_indexes, a)
        gt = int(gain > max_gain)
        max_gain = gt * gain + (1 - gt) * max_gain
        best = gt * a + (1 - gt) * best
    return best

def most_common_label(example_indexes):
    label_column = [row[class_attribute] for row in original_examples]
    num_of_classes = len(possible_values[class_attribute])
    label_counts = [0]*num_of_classes
    for index in range(len(example_indexes)):
        label = label_column[index] * (example_indexes[index] != 0) + (-1) * (example_indexes[index] == 0)
        label_index = 0;
        if label != -1:
            label_index = possible_values[class_attribute].index(label)
        label_counts[label_index] += 1 * (label != -1)
    return label_counts.index(max(label_counts))

def entropy(example_indexes):
    entropy = 0.0
    label_column = [row[class_attribute] for row in original_examples]
    for value in possible_values[class_attribute]:
        if value == -1:
            continue
        count = 0
        for index in range(len(example_indexes)):
            count += (label_column[index] == value) * (example_indexes[index] != 0)
        percentage = float(count) / sum(example_indexes)
        neq = int(percentage != 0)
        if percentage != 0:
            entropy -= neq * (percentage * math.log(percentage, 2))
    return entropy

def information_gain(example_indexes, attribute):
    gain = entropy(example_indexes)
    attribute_index = original_attributes.index(attribute)
    attribute_column = [row[attribute_index] for row in original_examples]
    for i in range(len(possible_values[attribute])):
        value = possible_values[attribute][i]
        if value == -1:
            continue
        subset = [0]*len(original_examples)
        for index in range(len(example_indexes)): # maybe simd
            subset[index] += (attribute_column[index] == value) * (example_indexes[index] != 0)
        percentage = float(sum(subset)) / sum(example_indexes)
        neq = int(percentage != 0)
        if percentage != 0:
            gain -= neq * (percentage * entropy(subset))
    return gain

def id3(example_indexes, attributes):
    if all_examples_same(example_indexes):
        label = -1
        label_column = [row[class_attribute] for row in original_examples]
        for index in range(len(example_indexes)):
            neq = (example_indexes[index] != 0)
            label = neq * label_column[index]+ (1-neq)*(label)
        return label
    if len(attributes) == 0:
        return most_common_label(example_indexes)
    best_attribute = best(example_indexes, attributes) #find best attribute
    best_attribute_original_index = original_attributes.index(best_attribute)
    best_attribute_index = attributes.index(best_attribute)
    branches = []
    best_attribute_column = [row[best_attribute_original_index] for row in original_examples]
    for value in possible_values[best_attribute]:
        if value == -1:
            continue
        branch = '[ ' + str(best_attribute) + ' == ' + str(value) +' ]'
        subset = [0] * len(original_examples)
        for index in range(len(example_indexes)):
            subset[index] += (best_attribute_column[index] == value) * (example_indexes[index] != 0)
        if sum(subset) == 0:
            branch += ' --> ' + str(most_common_label(example_indexes))
        else:
            branch += ' --> ' + str(id3(subset, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
        branches.append(branch)
    root = '{ '+ ' '.join(branches) +' }'
    return root

original_subset = [1]*len(original_examples)
print(id3(original_subset,original_attributes[:-1]))