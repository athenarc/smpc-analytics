import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

domain pd_shared3p shared3p;

/**
 * ID3 Summary
 * 1. Calculate the entropy of every attribute using the data set
 * 2. Split the set into subsets using the attribute for which the resulting entropy
 * 	  (after splitting) is minimum (or, equivalently, information gain is maximum)
 * 3. Make a decision tree node containing that attribute
 * 4. Recurse on subsets using remaining attributes.
**/

uint64 rows = 14;
uint64 columns = 5;
uint64 max_attribute_values = 3;
uint64 class_index = columns-1;
pd_shared3p uint64[[1]] original_attributes(columns) = {0,1,2,3,4}; //private?
pd_shared3p int64[[2]] original_examples(rows,columns) = reshape({0,0,1,0,1,
                                                                    0,0,1,1,1,
                                                                    1,0,1,0,0,
                                                                    2,1,1,0,0,
                                                                    2,2,0,0,0,
                                                                    2,2,0,1,1,
                                                                    1,2,0,1,0,
                                                                    0,1,1,0,1,
                                                                    0,2,0,0,0,
                                                                    2,1,0,0,0,
                                                                    0,1,0,1,0,
                                                                    1,1,1,1,0,
                                                                    1,0,0,0,0,
                                                                    2,1,1,1,1}, rows, columns);

pd_shared3p int64[[2]] possible_values(columns,max_attribute_values) = reshape({0,1,2,
                                                                                0,1,2,
                                                                                0,1,-1,
                                                                                0,1,-1,
                                                                                0,1,-1}, columns, max_attribute_values);

template <domain D, type T>
D uint64 index_of(D T[[1]] arr, D T element) {
    D uint64 idx = 0;
    for (uint64 i = 1; i < size(arr); i++) {
        D uint64 eq = (uint64)(arr[i] == element);
        idx = eq * i + (1-eq) * idx;
    }
    return idx;
}

pd_shared3p float64 log2(pd_shared3p float64 n){
    pd_shared3p float64[[1]] base2 = {2};
    pd_shared3p float64[[1]] n_arr = {n};
    pd_shared3p bool neq = (n != 0);
    n_arr[0] += (float64)(1-(uint64)neq);
    return log(n_arr, base2)[0];
}

pd_shared3p uint64 mylen(pd_shared3p int64[[2]] array){
    pd_shared3p uint64 len = 0;
    uint64[[1]] dims = shape(array);
    for(uint64 i = 0; i < dims[0]; i++){
        len += (uint64)(array[i,0] != -1);
    }
    return len;
}

pd_shared3p uint64 mylen(pd_shared3p int64[[1]] array){
    pd_shared3p uint64 len = 0;
    for(uint64 i = 0; i < size(array); i++){
        len += (uint64)(array[i] != -1);
    }
    return len;
}

pd_shared3p bool all_examples_same(pd_shared3p int64[[2]] examples) {
    uint64[[1]] dims = shape(examples);
    uint64 rows = dims[0];
    uint64 columns = dims[1];
    pd_shared3p uint64 res = 0;
    pd_shared3p uint64[[1]] class_counts(max_attribute_values);
    for (uint64 c = 0; c < max_attribute_values; c++) {
      	pd_shared3p int64 label = possible_values[class_index, c];
      	pd_shared3p bool neq = (label != -1);
        for (uint64 i = 0; i < rows; i++) {
            pd_shared3p bool eq = (examples[i,columns-1] == label);
            class_counts[c] += (uint64)neq*(uint64)(eq); // counter for class i
        }
        res += (uint64)(class_counts[c] == mylen(examples));
    }
    return (bool)res;
}

pd_shared3p float64 entropy(pd_shared3p int64[[2]] examples) {
    uint64[[1]] dims = shape(examples);
    uint64 rows = dims[0];
    uint64 columns = dims[1];

    pd_shared3p float64 entropy = 0.0;
    for (uint64 c = 0; c < max_attribute_values; c++) {
        pd_shared3p uint64 count = 0;
        pd_shared3p int64 label = possible_values[class_index, c];
        pd_shared3p bool neq = (label != -1);
        for (uint64 i = 0 ; i < rows ; i++) {
            count += (uint64)neq * (uint64)(examples[i, columns-1] == label);
        }
        pd_shared3p float64 percentage = (float64)count / (float64)mylen(examples);
        entropy -= (percentage * log2(percentage));
    }
    return entropy;
}

pd_shared3p float64 information_gain(pd_shared3p int64[[2]] examples, pd_shared3p uint64 attribute){
    pd_shared3p float64 gain = entropy(examples);
    pd_shared3p int64[[1]] attribute_values(max_attribute_values);
    for (uint64 i = 0; i < columns; i++) {
        pd_shared3p bool eq = (attribute == i);
        attribute_values += (int64)eq * possible_values[i,:]; // simd
    }
    for (uint64 v = 0; v < max_attribute_values; v++) {
        pd_shared3p int64 value = attribute_values[v];
        pd_shared3p int64[[2]] subset(rows,columns);
        pd_shared3p int64[[1]] minus_ones = reshape(-1,columns);
        for(uint64 i = 0; i < rows; i++){
            pd_shared3p int64[[1]] example = examples[i,:];
            pd_shared3p uint64 eq = 0;
            for (uint64 j = 0 ; j < columns ; j++) {
                eq += (uint64)(example[j] == value) * (uint64)(j == attribute);
            }
            subset[i,:] = (int64)eq * example + (int64)(1-eq) * minus_ones; //simd
        }
        pd_shared3p float64 percentage = (float64)mylen(subset) / (float64)mylen(examples);
        pd_shared3p bool neq = (percentage != 0);
        gain -= (float64)neq * percentage * entropy(subset);
    }
    return gain;
}

pd_shared3p uint64 best(pd_shared3p int64[[2]] examples, pd_shared3p uint64[[1]] attributes) {
    pd_shared3p float64 max_gain = information_gain(examples, attributes[0]);
    pd_shared3p uint64 best = attributes[0];
    for (uint64 i = 1; i < size(attributes); i++){
        pd_shared3p uint64 a = attributes[i];
        pd_shared3p float64 gain = information_gain(examples, a);
        pd_shared3p float64 gt = (float64)(gain > max_gain);
        max_gain = gt * gain + (1 - gt) * max_gain;
        best = (uint64)gt * a + (uint64)(1 - gt) * best;
    }
    return best;
}


pd_shared3p int64 most_common_label(pd_shared3p int64[[2]] examples){
    pd_shared3p int64[[1]] possible_classes = possible_values[class_index,:];
    pd_shared3p uint64[[1]] label_counts(max_attribute_values);
    for (uint64 i = 0; i < rows; i++) {
        pd_shared3p int64[[1]] example = examples[i,:];
        pd_shared3p int64 label = example[class_index];
        pd_shared3p uint64 label_index = index_of(possible_classes, label); //needs optimization
        for (uint64 c = 0; c < max_attribute_values; c++){ //maybe simd
            pd_shared3p bool eq = (label_index == c);
            label_counts[c] += (uint64)eq;
        }
    }
    pd_shared3p uint64 max_count = max(label_counts); //needs optimization
    return (int64)index_of(label_counts, max_count);
}

// pd_shared3p xor_uint8[[1]] result = bl_str("sun");
// pd_shared3p xor_uint8[[1]] r2 = bl_str("{}");
// result = bl_strCat(result, r2);
// print(bl_strDeclassify(result));

void main() {
    print(arrayToString(declassify(original_examples)));
    print(declassify(all_examples_same(original_examples)));
    print(declassify(entropy(original_examples)));
    pd_shared3p uint64 at = 3;
    print(declassify(information_gain(original_examples, at)));
    print(declassify(best(original_examples, original_attributes[1:4])));
    print(declassify(most_common_label(original_examples)));
}



