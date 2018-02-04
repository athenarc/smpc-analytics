import math

original_attributes = ['Outlook','Temperature','Humidity','Wind','Play ball?']

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

possible_values = {'Outlook':[0, 1, 2],
                    'Temperature':[0, 1, 2],
                    'Humidity':[0, 1],
                    'Wind':[0, 1],
                    'Play ball?':[0, 1]}
class_attribute = 'Play ball?'

def mylen(data):
    len = 0
    for d in data:
        len += (d[0] != -1)
    return len

def all_examples_same(examples):
    res = 0
    class_counts = [0]*len(possible_values[class_attribute])
    for i in range(len(possible_values[class_attribute])):
        for example in examples:
            class_counts[i] += int(example[-1] == i)
        res += int(class_counts[i] == mylen(examples))
    return res

def best(examples, attributes):
    max_gain = information_gain(examples, attributes[0])
    best = attributes[0]
    for i in range(1, len(attributes)):
        a = attributes[i]
        gain = information_gain(examples, a)
        gt = int(gain > max_gain)
        max_gain = gt * gain + (1 - gt) * max_gain
        best = gt * a + (1 - gt) * best
    return best

def most_common_label(examples):
    num_of_classes = len(possible_values[class_attribute])
    label_counts = [0]*num_of_classes # array of 2 values (Yes:0, No:0)
    for i in range(len(examples)):
        example = examples[i]
        class_attribute_index = len(example)-1
        label = example[class_attribute_index]
        label_index = 0;
        if label != -1:
            label_index = possible_values[class_attribute].index(label)
        label_counts[label_index] += 1 * (label == -1)
    return label_counts.index(max(label_counts))

def entropy(examples):
    entropy = 0.0
    for value in possible_values[class_attribute]: # [Yes, No]
        count = 0
        for example in examples:
            count += example[len(example)-1] == value
        percentage = float(count) / mylen(examples)
        neq = int(percentage != 0)
        if percentage != 0:
            entropy -= neq * (percentage * math.log(percentage, 2))
    return entropy

def information_gain(examples, attribute):
    gain = entropy(examples)
    attribute_index = original_attributes.index(attribute)
    for i in range(len(possible_values[attribute])):
        value = possible_values[attribute][i]
        subset = [[-1]*len(original_examples[0]) for _ in range(len(original_examples))]
        for j in range(len(original_examples)):
            example = examples[j]
            eq = example[attribute_index] == value
            for k in range(len(example)): #can be done with simd
                subset[j][k] = eq*example[k] + (1-eq)*(-1)
        percentage = float(mylen(subset)) / mylen(examples)
        neq = int(percentage != 0)
        if percentage != 0:
            gain -= neq * (percentage * entropy(subset))
    return gain

def id3(examples, attributes):
    if all_examples_same(examples):
        label = -1
        for example in examples:
            neq = int(example[-1] != -1)
            label = neq * example[-1] + (1-neq)*(label)
        return label
    if len(attributes) == 0:
        return ''
    best_attribute = best(examples, attributes) #find best attribute
    best_attribute_original_index = original_attributes.index(best_attribute)
    best_attribute_index = attributes.index(best_attribute)
    branches = []
    for value in possible_values[best_attribute]:
        branch = '[' + best_attribute + ' == ' + str(value) +']'
        subset = [[-1] * len(original_examples[0]) for _ in range(len(original_examples))]
        for j in range(len(original_examples)):
            example = examples[j]
            eq = example[best_attribute_original_index] == value
            for k in range(len(example)): #can be done with simd
                subset[j][k] = eq * example[k] + (1-eq) * (-1)
        if mylen(subset) == 0:
            branch += ' --> ' + str(most_common_label(examples))
        else:
            branch += ' --> ' + str(id3(subset, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))

        branches.append(branch)
    root = '{'+ ','.join(branches) +'}'
    return root


print(id3(original_examples,original_attributes[:-1]))
