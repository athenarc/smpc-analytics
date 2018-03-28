import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

import oblivious;
import shared3p_oblivious;

import data_input;

/**
 * ID3 Summary
 * 1. Calculate the entropy of every attribute using the data set
 * 2. Split the set into subsets using the attribute for which the resulting entropy
 * 	  (after splitting) is minimum (or, equivalently, information gain is maximum)
 * 3. Make a decision tree node containing that attribute
 * 4. Recurse on subsets using remaining attributes.
**/

// uint64 rows = 14;
// uint64 columns = 5;
// uint64 max_attribute_values = 3;
// uint64 class_index = columns-1;
// pd_shared3p uint64[[1]] original_attributes(columns) = {0,1,2,3,4}; //private? //iota
// pd_shared3p int64[[2]] original_examples(rows,columns) = reshape({0,0,1,0,1,
//                                                                     0,0,1,1,1,
//                                                                     1,0,1,0,0,
//                                                                     2,1,1,0,0,
//                                                                     2,2,0,0,0,
//                                                                     2,2,0,1,1,
//                                                                     1,2,0,1,0,
//                                                                     0,1,1,0,1,
//                                                                     0,2,0,0,0,
//                                                                     2,1,0,0,0,
//                                                                     0,1,0,1,0,
//                                                                     1,1,1,1,0,
//                                                                     1,0,0,0,0,
//                                                                     2,1,1,1,1}, rows, columns);
//
// pd_shared3p int64[[2]] possible_values(columns,max_attribute_values) = reshape({0,1,2,
//                                                                                 0,1,2,
//                                                                                 0,1,-1,
//                                                                                 0,1,-1,
//                                                                                 0,1,-1}, columns, max_attribute_values);


template <type T>
pd_shared3p xor_uint8[[1]] itoa(pd_shared3p T x){
    pd_shared3p uint8[[1]] stru(20);
    uint[[1]] div = {10000000000000000000,1000000000000000000,100000000000000000,10000000000000000,1000000000000000,100000000000000,10000000000000,1000000000000,100000000000,10000000000,1000000000,100000000,10000000,1000000,100000,10000,1000,100,10,1};
    stru = (uint8) (((uint64)x / div) % 10);

    // Number of zeroes on the left
    pd_shared3p bool[[1]] mask = stru == 0;
    pd_shared3p uint8 nzero = (uint8) truePrefixLength(mask);

    // Add ASCII offset to non-zero symbols
    pd_shared3p uint8[[1]] idx(20);
    for (uint i = 0; i < 20; ++i) {
        idx[i] = (uint8) i;
    }
    mask = idx < nzero;

    pd_shared3p uint8[[1]] zero(20) = 0;
    pd_shared3p uint8[[1]] offset(20) = 48;
    stru = stru + choose(mask, zero, offset);
    pd_shared3p xor_uint8[[1]] str = reshare(stru);

    // Rotate left so that the zeroes would move to the right
    idx -= nzero;
    pd_shared3p xor_uint8[[2]] mat(20, 2);
    mat[:, 0] = reshare(idx);
    mat[:, 1] = str;
    str = quicksort(mat, 0 :: uint, true)[:, 1];
    uint64 bound = 20;
    pd_shared3p xor_uint8[[1]] zero_string(20) = bl_str("0", bound);

    pd_shared3p bool eqz = (x == 0);
    pd_shared3p uint8[[1]] res = choose(eqz, reshare(zero_string), reshare(str));
    return reshare(res);
}

template <domain D, type T>
D uint64 index_of(D T[[1]] arr, D T element) {
    D uint64 idx = 0;
    D uint64 cnt = 0;
    D uint64 found = 0;
    for (uint64 i = 1; i < size(arr); i++) {
        D uint64 eq = (uint64)(arr[i] == element);
        cnt += eq;
        idx = (1-found) * (eq * i + (1-eq) * idx) + found * idx;
        found = (uint64)(cnt > 0);
    }
    return idx;
}


pd_shared3p float64 log2(pd_shared3p float64 n) {
    pd_shared3p float64[[1]] base2 = {2};
    pd_shared3p float64[[1]] n_arr = {n};
    pd_shared3p bool neq = (n != 0);
    n_arr[0] += (float64)(1-(uint64)neq);
    return log(n_arr, base2)[0];
}


pd_shared3p uint64 count_positives(pd_shared3p int64[[2]] array) {
    pd_shared3p uint64 len = 0;
    uint64[[1]] dims = shape(array);
    for(uint64 i = 0; i < dims[0]; i++){
        len += (uint64)(array[i,0] != -1);
    }
    return len;
}


pd_shared3p uint64 count_positives(pd_shared3p int64[[1]] array) {
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
        res += (uint64)(class_counts[c] == count_positives(examples));
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
        pd_shared3p float64 percentage = (float64)count / (float64)count_positives(examples);
        entropy -= (percentage * log2(percentage));
    }
    return entropy;
}


pd_shared3p float64 information_gain(pd_shared3p int64[[2]] examples, pd_shared3p uint64 attribute) {
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
        for (uint64 i = 0; i < rows; i++){
            pd_shared3p int64[[1]] example = examples[i,:];
            pd_shared3p uint64 eq = 0;
            for (uint64 j = 0 ; j < columns ; j++) {
                eq += (uint64)(example[j] == value) * (uint64)(j == attribute);
            }
            subset[i,:] = (int64)eq * example + (int64)(1-eq) * minus_ones; //simd
        }
        pd_shared3p float64 percentage = (float64)count_positives(subset) / (float64)count_positives(examples);
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


pd_shared3p int64 most_common_label(pd_shared3p int64[[2]] examples) {
    pd_shared3p int64[[1]] possible_classes = possible_values[class_index,:];
    pd_shared3p uint64[[1]] label_counts(max_attribute_values);
    for (uint64 i = 0; i < rows; i++) {
        pd_shared3p int64[[1]] example = examples[i,:];
        pd_shared3p int64 label = example[class_index];
        pd_shared3p bool neq = (label != -1);
        pd_shared3p uint64 label_index = index_of(possible_classes, label); //needs optimization
        for (uint64 c = 0; c < max_attribute_values; c++) { //maybe simd
            pd_shared3p bool eq = (label_index == c);
            label_counts[c] += (uint64)neq*(uint64)(eq);
        }
    }
    pd_shared3p uint64 max_count = max(label_counts); //needs optimization
    return (int64)index_of(label_counts, max_count);
}


pd_shared3p xor_uint8[[1]] id3(pd_shared3p int64[[2]] examples, pd_shared3p uint64[[1]] attributes) {
    if (declassify(all_examples_same(examples))) {
        pd_shared3p int64 label = -1;
        for (uint64 i = 0; i < rows; i++) {
            pd_shared3p int64[[1]] example = examples[i,:];
            pd_shared3p bool neq = example[class_index] != -1;
            label = (int64)neq * example[class_index] + (1-(int64)neq)*(label);
        }
        return itoa(label);
    }
    if (size(attributes) == 0) {
        return itoa(most_common_label(examples));
    }
    pd_shared3p uint64 best_attribute = best(examples, attributes); // find best attribute
    pd_shared3p uint64 best_attribute_original_index = index_of(original_attributes, best_attribute); // maybe 1 for loop
    pd_shared3p uint64 best_attribute_index = index_of(attributes, best_attribute);
    pd_shared3p xor_uint8[[1]] branches;
  	pd_shared3p int64[[1]] best_attribute_values(max_attribute_values);
    for (uint64 i = 0; i < columns; i++) {
        pd_shared3p bool eq = (i == best_attribute_original_index);
      	best_attribute_values += (int64)eq * possible_values[i,:]; // simd
    }

  	for (uint64 v = 0 ; v < max_attribute_values ; v++) {
		    pd_shared3p int64 value = best_attribute_values[v];
        if (declassify(value == -1)) {
            continue;
        }
        pd_shared3p int64[[2]] subset(rows,columns);
        pd_shared3p int64[[1]] minus_ones = reshape(-1,columns);
        for(uint64 i = 0; i < rows; i++){
            pd_shared3p int64[[1]] example = examples[i,:];
            pd_shared3p uint64 eq = 0;
            for (uint64 j = 0 ; j < columns ; j++) {
                eq += (uint64)(example[j] == value) * (uint64)(j == best_attribute_original_index);
            }
            subset[i,:] = (int64)eq * example + (int64)(1-eq) * minus_ones; // simd
        }
        pd_shared3p xor_uint8[[1]] branch = bl_strCat(left_br_str, itoa(best_attribute));
        branch = bl_strCat(branch, eq_str);
        branch = bl_strCat(branch, itoa(value));
        branch = bl_strCat(branch, right_br_str);
        branch = bl_strCat(branch, arrow_str);

      	if (declassify(count_positives(subset) == 0)) {
            branch = bl_strCat(branch, itoa(most_common_label(examples)));
        } else {
            pd_shared3p int64[[1]] first_half(size(attributes));
            pd_shared3p int64[[1]] second_half(size(attributes));
            for (uint64 i = 0; i < size(attributes); i++) { // Fill first & second
                pd_shared3p bool lt = (i < best_attribute_index);
                pd_shared3p bool gt = (i > best_attribute_index);
                first_half[i] += (int64)lt * (int64)attributes[i] + (1-(int64)lt) * (-1);
                second_half[i] += (int64)gt * (int64)attributes[i] + (1-(int64)gt) * (-1);
            }
            pd_shared3p int64[[1]] new_attribs(size(attributes)-1) = first_half[:size(attributes)-1];
            for (uint64 i = size(attributes)-1; i > 0; i--) {
                pd_shared3p bool neq = (second_half[i] != -1);
                new_attribs[i-1] += (int64)neq * (1+second_half[i]);
            }

            branch = bl_strCat(branch, id3(subset, (uint64)new_attribs));
        }
        branches = bl_strCat(branches, branch);
        branches = bl_strCat(branches, space_str);
    }

    pd_shared3p xor_uint8[[1]] root = bl_strCat(left_curly_br_str, branches);
    return bl_strCat(root, right_curly_br_str);
}

void main() {
    left_br_str = bl_str("[ ");
    right_br_str = bl_str(" ]");
    eq_str = bl_str(" == ");
    space_str = bl_str(" ");
    arrow_str = bl_str(" --> ");
    left_curly_br_str = bl_str("{ ");
    right_curly_br_str = bl_str("}");

    pd_shared3p xor_uint8[[1]] root = id3(original_examples, original_attributes[:columns-1]);
    print(bl_strDeclassify(root));
}

pd_shared3p xor_uint8[[1]] left_br_str;
pd_shared3p xor_uint8[[1]] right_br_str;
pd_shared3p xor_uint8[[1]] eq_str;
pd_shared3p xor_uint8[[1]] space_str;
pd_shared3p xor_uint8[[1]] arrow_str;
pd_shared3p xor_uint8[[1]] left_curly_br_str;
pd_shared3p xor_uint8[[1]] right_curly_br_str;
