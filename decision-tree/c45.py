import math

original_attributes = ['petal length', 'petal width', 'sepal width', 'sepal length', 'flower']

examples = [[4.3, 3.0, 1.1, 0.1, 'Iris-setosa'],
 [4.8, 3.0, 1.4, 0.1, 'Iris-setosa'],
 [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
 [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
 [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
 [5.2, 4.1, 1.5, 0.1, 'Iris-setosa'],
 [4.6, 3.6, 1.0, 0.2, 'Iris-setosa'],
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

# examples = [[5.1, 3.5, 1.4, 0.2, 'Iris-setosa'], [4.9, 3.0, 1.4, 0.2, 'Iris-setosa'], [4.7, 3.2, 1.3, 0.2, 'Iris-setosa'], [4.6, 3.1, 1.5, 0.2, 'Iris-setosa'], [5.0, 3.6, 1.4, 0.2, 'Iris-setosa'], [5.4, 3.9, 1.7, 0.4, 'Iris-setosa'], [4.6, 3.4, 1.4, 0.3, 'Iris-setosa'], [5.0, 3.4, 1.5, 0.2, 'Iris-setosa'], [4.4, 2.9, 1.4, 0.2, 'Iris-setosa'], [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'], [7.0, 3.2, 4.7, 1.4, 'Iris-versicolor'], [6.4, 3.2, 4.5, 1.5, 'Iris-versicolor'], [6.9, 3.1, 4.9, 1.5, 'Iris-versicolor'], [5.5, 2.3, 4.0, 1.3, 'Iris-versicolor'], [6.5, 2.8, 4.6, 1.5, 'Iris-versicolor'], [5.7, 2.8, 4.5, 1.3, 'Iris-versicolor'], [6.3, 3.3, 4.7, 1.6, 'Iris-versicolor'], [4.9, 2.4, 3.3, 1.0, 'Iris-versicolor'], [6.6, 2.9, 4.6, 1.3, 'Iris-versicolor'], [5.2, 2.7, 3.9, 1.4, 'Iris-versicolor'], [6.3, 3.3, 6.0, 2.5, 'Iris-virginica'], [5.8, 2.7, 5.1, 1.9, 'Iris-virginica'], [7.1, 3.0, 5.9, 2.1, 'Iris-virginica'], [6.3, 2.9, 5.6, 1.8, 'Iris-virginica'], [6.5, 3.0, 5.8, 2.2, 'Iris-virginica'], [7.6, 3.0, 6.6, 2.1, 'Iris-virginica'], [4.9, 2.5, 4.5, 1.7, 'Iris-virginica'], [7.3, 2.9, 6.3, 1.8, 'Iris-virginica'], [6.7, 2.5, 5.8, 1.8, 'Iris-virginica'], [7.2, 3.6, 6.1, 2.5, 'Iris-virginica']]

#SMALL
# examples = [[4.3,3.0,1.1,0.1,'Iris-setosa'],
# [4.8,3.0,1.4,0.1,'Iris-setosa'],
# [4.9,3.1,1.5,0.1,'Iris-setosa'],
# [4.9,3.1,1.5,0.1,'Iris-setosa'],
# [4.9,3.1,1.5,0.1,'Iris-setosa'],
# [5.2,4.1,1.5,0.1,'Iris-setosa'],
# [4.6,3.6,1.0,0.2,'Iris-setosa'],
# [5.0,3.2,1.2,0.2,'Iris-setosa'],
# [5.8,4.0,1.2,0.2,'Iris-setosa'],
# [4.4,3.0,1.3,0.2,'Iris-setosa'],
# [5.0,2.3,3.3,1.0,'Iris-versicolor'],
# [4.9,2.4,3.3,1.0,'Iris-versicolor'],
# [5.0,2.0,3.5,1.0,'Iris-versicolor'],
# [5.7,2.6,3.5,1.0,'Iris-versicolor'],
# [5.5,2.4,3.7,1.0,'Iris-versicolor'],
# [6.0,2.2,4.0,1.0,'Iris-versicolor'],
# [5.8,2.7,4.1,1.0,'Iris-versicolor'],
# [5.1,2.5,3.0,1.1,'Iris-versicolor'],
# [5.5,2.4,3.8,1.1,'Iris-versicolor'],
# [5.6,2.5,3.9,1.1,'Iris-versicolor'],
# [6.4,2.8,5.6,2.1,'Iris-virginica'],
# [6.7,3.3,5.7,2.1,'Iris-virginica'],
# [7.1,3.0,5.9,2.1,'Iris-virginica'],
# [7.6,3.0,6.6,2.1,'Iris-virginica'],
# [6.4,2.8,5.6,2.2,'Iris-virginica'],
# [6.5,3.0,5.8,2.2,'Iris-virginica'],
# [7.7,3.8,6.7,2.2,'Iris-virginica'],
# [6.9,3.1,5.1,2.3,'Iris-virginica'],
# [6.7,3.0,5.2,2.3,'Iris-virginica'],
# [6.4,3.2,5.3,2.3,'Iris-virginica']]
# possible_values = {'Outlook':['Sunny', 'Overcast', 'Rain'],
#                     'Temperature':['Hot', 'Mild', 'Cool'],
#                     'Humidity':['Normal', 'High'],
#                     'Wind':['Weak', 'Strong'],
#                     'Play ball?':['Yes', 'No']}
possible_values = {'sepal length': 'continuous',
'sepal width': 'continuous',
'petal length': 'continuous',
'petal width': 'continuous',
'flower' : ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']}

categorical_attributes = ['flower']

# class_attribute = 'Play ball?'
class_attribute = 'flower'

def log_2(x):
    if x != 0:
        # print "---- log(", x, ")"
        return math.log(x, 2)
    return 0

def all_examples_same(examples):
    same = True
    for i in range(len(examples)-1):
        example1 = examples[i]
        example2 = examples[i+1]
        same = same and example1[-1] == example2[-1]
    return same


def split_attribute(examples, attributes):
    max_gain = -1 * float('inf')
    best_threshold = -1
    best_attribute = -1
    best_splitted = -1
    
    ent, counts = entropy(examples)
    gain, entropy_less, entropy_greater = -1, -1, -1
    
    for attribute in attributes:
        attribute_index = attribute_index = original_attributes.index(attribute)
        if attribute in categorical_attributes:
            splitted = []
            for value in possible_values[attribute]:
                subset = [example for example in examples if example[attribute_index] == value] # subset of examples that have attribute = value
                splitted.append(subset)
                
            gain = information_gain(ent, len(examples), splitted)
            if gain > max_gain:
                max_gain = gain
                best_attribute = attribute
                best_splitted = splitted
        else:
            splitted, difference = [], []
            counts_less, counts_greater = [0], [0]
            examples = sorted(examples, key=lambda l:l[attribute_index])
            for i in range(len(examples)-1):
                example = examples[i]
                next_example = examples[i+1]
                if example[attribute_index] != next_example[attribute_index]:
                    threshold = (example[attribute_index] + next_example[attribute_index]) / 2
                    less = []
                    greater = []
                    for e in examples:
                        if e[attribute_index] > threshold:
                            greater.append(e)
                        else:
                            less.append(e)
                    
                    prev_splitted = splitted    # store the previous subsets
                    splitted = [less, greater]  # update the new ones
                    
                    if prev_splitted != []:
                        new_elems = len(splitted[0]) - len(prev_splitted[0])    # check the difference in the less subsets
                        difference = splitted[0][-1 * new_elems:]              # keep the last new elements of the less list

                    gain, entropy_less, entropy_greater, counts_less, counts_greater = information_gain_incremental(ent, len(examples), splitted, difference, counts_less, counts_greater, prev_splitted == [] )
                    
                
                    if gain > max_gain:
                        max_gain = gain
                        best_attribute = attribute
                        best_threshold = threshold
                        best_splitted = splitted
                    
    return best_attribute, best_threshold, best_splitted


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
    counts = []
    for value in possible_values[class_attribute]: # [Yes, No]
        count = sum([1 for example in examples if example[-1] == value]) # count occurencies of value in examples
        percentage = float(count) / len(examples)
        entropy -= (percentage * log_2(percentage))
        counts.append(count)
    return entropy, counts


def information_gain(gain, length, subsets):
    for subset in subsets:
        percentage = float(len(subset)) / length
        if percentage != 0:
            gain -= (percentage*entropy(subset))
    return gain


def combine_entropies(difference, total_length, prev_counts, addition):
    e = 0.0
    if len(difference) != 0:
        entropy_diff, counts_diff = entropy(difference) # No need to calculate entropy_diff. Just counts
        # if we are dealing with the less subset
        if addition:
            counts = [count_prev + count_diff for count_diff, count_prev in zip(counts_diff, prev_counts)]
        else:
            counts = [count_prev - count_diff for count_diff, count_prev in zip(counts_diff, prev_counts)]
    else:
        counts = prev_counts
    percentages = [float(count) / total_length for count in counts]
    e = - sum([p * log_2(p) for p in percentages])
        
    return e, counts


def information_gain_incremental(gain, length, splitted, difference, counts_less, counts_greater, first_iteration):
    # less
    percentage = float(len(splitted[0])) / length
    if percentage != 0:
        if first_iteration:
            entropy_less, counts_less = entropy(splitted[0])
        else:
            entropy_less, counts_less = combine_entropies(difference, len(splitted[0]), counts_less, True)
        gain -= (percentage * entropy_less)
        
    # greater
    percentage = float(len(splitted[1])) / length
    if percentage != 0:
        if first_iteration:
            entropy_greater, counts_greater = entropy(splitted[1])
        else:
            entropy_greater, counts_greater  = combine_entropies(difference, len(splitted[1]), counts_greater, False)
        gain -= (percentage * entropy_greater)
        
    return gain, entropy_less, entropy_greater, counts_less, counts_greater



def c45(examples, attributes):
    if all_examples_same(examples):
        label = examples[0][-1]
        return label
    if len(attributes) == 0:
        return str(most_common_label(examples))
    best_attribute, best_threshold, splitted = split_attribute(examples, attributes) #find best attribute
    best_attribute_original_index = original_attributes.index(best_attribute)
    best_attribute_index = attributes.index(best_attribute)
    branches = []
    if best_attribute in categorical_attributes:
        for i in range(len(possible_values[best_attribute])):
            value = possible_values[best_attribute][i]
            branch = '"' + str(best_attribute)+' == '+str(value) + '"'
            subset = splitted[i]
            if len(subset) == 0:
                branch += ' : ' + str(most_common_label(examples))
            else:
                branch  += ' : ' + str(c45(subset, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
            branches.append(branch)
    else:
        branch = '"' + str(best_attribute)+' <= '+str(best_threshold) + '"'
        less = splitted[0]
        if len(less) == 0:
            branch += ' : ' + str(most_common_label(examples))
        else:
            branch  += ' : ' + str(c45(less, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
        branches.append(branch)
        branch = '"' + str(best_attribute)+' > '+str(best_threshold) + '"'
        greater = splitted[1]
        if len(greater) == 0:
            branch += ' : ' + str(most_common_label(examples))
        else:
            branch  += ' : ' + str(c45(greater, attributes[:best_attribute_index]+attributes[best_attribute_index+1:]))
        branches.append(branch)
    root = '{ '+ ', '.join(branches) +' }'
    return root

print(c45(examples,original_attributes[:-1]))