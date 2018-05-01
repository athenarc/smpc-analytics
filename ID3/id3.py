import math

original_attributes = ['Outlook','Temperature','Humidity','Wind','Play ball?']

examples = [['Sunny','Hot','High','Weak','No'],
            ['Sunny','Hot','High','Strong','No'],
            ['Overcast','Hot','High','Weak','Yes'],
            ['Rain','Mild','High','Weak','Yes'],
            ['Rain','Cool','Normal','Weak','Yes'],
            ['Rain','Cool','Normal','Strong','No'],
            ['Overcast','Cool','Normal','Strong','Yes'],
            ['Sunny','Mild','High','Weak','No'],
            ['Sunny','Cool','Normal','Weak','Yes'],
            ['Rain','Mild','Normal','Weak','Yes'],
            ['Sunny','Mild','Normal','Strong','Yes'],
            ['Overcast','Mild','High','Strong','Yes'],
            ['Overcast','Hot','Normal','Weak','Yes'],
            ['Rain','Mild','High','Strong','No']]


possible_values = {'Outlook':['Sunny', 'Overcast', 'Rain'],
                    'Temperature':['Hot', 'Mild', 'Cool'],
                    'Humidity':['Normal', 'High'],
                    'Wind':['Weak', 'Strong'],
                    'Play ball?':['Yes', 'No']}

class_attribute = 'Play ball?'

def all_examples_same(examples):
    same = True
    for i in range(len(examples)-1):
        example1 = examples[i]
        example2 = examples[i+1]
        same = same and example1[-1] == example2[-1]
    return same

def best(examples, attributes):
    max_gain = information_gain(examples, attributes[0])
    best = attributes[0]
    for i in range(1,len(attributes)):
        a = attributes[i]
        gain = information_gain(examples, a)
        if gain > max_gain:
            max_gain = gain
            best = a
    return best

def most_common_label(examples):
    label_counts = {}
    for example in examples:
        label = example[-1]
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 0
    return( max(label_counts, key=label_counts.get))

def entropy(examples):
    entropy = 0.0
    for value in possible_values[class_attribute]: # [Yes, No]
        count = sum([1 for example in examples if example[-1] == value]) # count occurencies of value in examples
        percentage = float(count) / len(examples)
        if percentage != 0:
            entropy -= (percentage * math.log(percentage, 2))
    return entropy

def information_gain(examples, attribute):
    gain = entropy(examples)
    attribute_index = original_attributes.index(attribute)
    for value in possible_values[attribute]:
        subset = [example for example in examples if example[attribute_index] == value] # subset of examples that have attribute = value
        percentage = float(len(subset)) / len(examples)
        if percentage != 0:
            gain -= (percentage*entropy(subset))
    return gain


def id3(examples, attributes):
    if all_examples_same(examples):
        label = examples[0][-1]
        return label
    if len(attributes) == 0:
        return str(most_common_label(examples))
    best_attribute = best(examples, attributes) #find best attribute
    best_attribute_original_index = original_attributes.index(best_attribute)
    best_attribute_index = attributes.index(best_attribute)
    branches = []
    for value in possible_values[best_attribute]:
        branch = '"' + str(best_attribute)+' == '+str(value) + '"'
        subset = [example for example in examples if example[best_attribute_original_index] == value]
        if len(subset) == 0:
            branch += ' : ' + str(most_common_label(examples))
        else:
            branch  += ' : ' + str(id3(subset, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
        branches.append(branch)
    root = '{ '+ ', '.join(branches) +' }'
    return root

print(id3(examples,original_attributes[:-1]))
