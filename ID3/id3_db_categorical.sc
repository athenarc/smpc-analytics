import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

import oblivious;
import shared3p_oblivious;

import shared3p_table_database;
import table_database;


domain pd_shared3p shared3p;



string datasource = "DS1";
// string table = "id3_data";


/**
 * ID3 Summary
 * 1. Calculate the entropy of every attribute using the data set
 * 2. Split the set into subsets using the attribute for which the resulting entropy
 *     (after splitting) is minimum (or, equivalently, information gain is maximum)
 * 3. Make a decision tree node containing that attribute
 * 4. Recurse on subsets using remaining attributes.
**/


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
D uint64 index_of_max(D T[[1]] arr) {
    D uint64 idx = 0;
    D T max = arr[0];
    for (uint64 i = 1; i < size(arr); i++) {
        D uint64 gt = (uint64)(arr[i] > max);
        max = gt * arr[i] + (1 - gt) * max;
        idx = gt * i + (1-gt) * idx;
    }
    return idx;
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

template <domain D, type T>
D T sum(D T[[2]] arr) {
    uint64[[1]] dims = shape(arr);
    D T sum = 0;
    for (uint64 i = 0; i < dims[0]; i++ ){
        sum += sum(arr[i,:]);
    }
    return sum;
}

// template <domain D, type T>
pd_shared3p int64 sum(uint64 vmap, uint64 len) {
    pd_shared3p int64 sum = 0;
    for (uint64 i = 0 ; i < len ; i++) {
        pd_shared3p int64[[1]] values = tdbVmapGetValue(vmap, "0", i :: uint64);
        sum += sum(values);
    }
    return sum;
}



pd_shared3p bool all_examples_same(uint64 example_indexes_vmap) {
    pd_shared3p uint64 res = 0;
    pd_shared3p uint64[[1]] class_counts(max_attribute_values);
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        pd_shared3p uint64 partial_res = 0;
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
        uint64 rows = tdbGetRowCount(datasource, table);
        uint64 columns = tdbGetColumnCount(datasource, table);
        pd_shared3p float64[[1]] label_column = tdbReadColumn(datasource, table, class_index);
        pd_shared3p int64 positive_indexes = sum(example_indexes);
        for (uint64 a = 0; a < max_attribute_values; a++) {
            pd_shared3p float64 label = possible_values[class_index, a];
            pd_shared3p uint64[[1]] eq = (uint64)(label_column == label) * (uint64)(example_indexes != 0) * (uint64)(label != -1);
            class_counts[a] = sum(eq);
            partial_res += (uint64)(class_counts[a] == (uint64) positive_indexes);
        }
        res += (uint64) (partial_res > 0);
    }
    return (res == data_providers_num);
}


pd_shared3p float64 entropy(uint64 example_indexes_vmap) {
    pd_shared3p float64 entropy = 0.0;
    pd_shared3p int64 total_count = 0;
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
        total_count += sum(example_indexes);
    }
    for (uint64 c = 0; c < max_attribute_values; c++) {
        pd_shared3p uint64 equal_count = 0;
        for (uint64 i = 0 ; i < data_providers_num ; i++) {
            string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
            pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
            uint64 rows = tdbGetRowCount(datasource, table);
            pd_shared3p float64[[1]] label_column = tdbReadColumn(datasource, table, class_index);
            pd_shared3p float64 label = possible_values[class_index, c];
            pd_shared3p uint64[[1]] eq = (uint64)(label_column == label) * (uint64)(example_indexes != 0) * (uint64)(label != -1);
            equal_count += sum(eq);
        }
        pd_shared3p float64 percentage = (float64)equal_count / (float64)total_count;
        entropy -= (percentage * log2(percentage));
    }
    return entropy;
}


pd_shared3p float64 information_gain(uint64 example_indexes_vmap, pd_shared3p uint64 attribute) {
    pd_shared3p float64 gain = entropy(example_indexes_vmap);
    pd_shared3p float64[[1]] attribute_values(max_attribute_values);
    pd_shared3p int64 total_count = 0;
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
        total_count += sum(example_indexes);
    }
    for (uint64 i = 0; i < columns; i++) {
        pd_shared3p bool eq = (attribute == i);
        attribute_values += (float64)eq * possible_values[i,:]; // simd
    }
    for (uint64 v = 0; v < max_attribute_values; v++) {
        pd_shared3p float64 value = attribute_values[v];
        uint64 subset = tdbVmapNew();
        pd_shared3p int64 subset_count = 0;
        for (uint64 i = 0 ; i < data_providers_num ; i++) {
            string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
            pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
            uint64 rows = tdbGetRowCount(datasource, table);
            pd_shared3p float64[[1]] attribute_column(rows);
            for (uint64 c = 0; c < columns; c++) {
                pd_shared3p bool eq = (attribute == c);
                attribute_column += (float64)eq * tdbReadColumn(datasource, table, c);
            }
            pd_shared3p int64[[1]] partial_subset(rows) = (int64)(attribute_column == value) * (int64)(example_indexes != 0);
            tdbVmapAddValue(subset, "0", partial_subset);
            subset_count += sum(partial_subset);
        }
        pd_shared3p float64 percentage = (float64)subset_count / (float64)total_count;
        pd_shared3p bool neq = (percentage != 0);
        gain -= (float64)neq * percentage * entropy(subset);
    }
    return gain;
}


pd_shared3p uint64 best(uint64 example_indexes_vmap, pd_shared3p uint64[[1]] attributes) {
    pd_shared3p float64 max_gain = information_gain(example_indexes_vmap, attributes[0]);
    pd_shared3p uint64 best = attributes[0];
    for (uint64 i = 1; i < size(attributes); i++){
        pd_shared3p uint64 a = attributes[i];
        pd_shared3p float64 gain = information_gain(example_indexes_vmap, a);
        pd_shared3p float64 gt = (float64)(gain > max_gain);
        max_gain = gt * gain + (1 - gt) * max_gain;
        best = (uint64)gt * a + (uint64)(1 - gt) * best;
    }
    return best;
}



pd_shared3p int64 most_common_label(uint64 example_indexes_vmap) {
    pd_shared3p uint64[[1]] label_counts(max_attribute_values);
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
        pd_shared3p float64[[1]] label_column = tdbReadColumn(datasource, table, class_index);
        for (uint64 a = 0; a < max_attribute_values; a++) {
            pd_shared3p uint64[[1]] eq = (uint64)((int64)label_column == (int64) a)* (uint64)(example_indexes != 0);
            label_counts[a] += sum(eq);
        }
    }
    return (int64)index_of_max(label_counts);
}


pd_shared3p xor_uint8[[1]] id3(uint64 example_indexes_vmap, pd_shared3p uint64[[1]] attributes) {
    if (declassify(all_examples_same(example_indexes_vmap))) {
        pd_shared3p int64 label_count = 0;
        pd_shared3p int64 total_count = 0;
        for (uint64 i = 0 ; i < data_providers_num ; i++) {
            string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
            pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
            pd_shared3p float64[[1]] label_column = tdbReadColumn(datasource, table, class_index);
            pd_shared3p float64[[1]] true_labels = (float64)example_indexes * label_column;
            label_count += (int64)sum(true_labels);
            total_count += sum(example_indexes);
        }
        pd_shared3p float64 label = (float64) ((uint64)label_count / (uint64)total_count);
        return itoa((int64)label);
    }
    if (size(attributes) == 0) {
        return itoa(most_common_label(example_indexes_vmap));
    }
    pd_shared3p uint64 best_attribute = best(example_indexes_vmap, attributes); // find best attribute
    pd_shared3p uint64 best_attribute_original_index = index_of(original_attributes, best_attribute); // maybe 1 for loop
    pd_shared3p uint64 best_attribute_index = index_of(attributes, best_attribute);
    pd_shared3p xor_uint8[[1]] branches;
    pd_shared3p float64[[1]] best_attribute_values(max_attribute_values);
    for (uint64 j = 0; j < columns; j++) {
        pd_shared3p bool eq = (j == best_attribute_original_index);
        best_attribute_values += (float64)eq * possible_values[j,:]; // simd
    }
    for (uint64 v = 0 ; v < max_attribute_values ; v++) {
        pd_shared3p float64 value = best_attribute_values[v];
        if (declassify(value == -1)) {
            continue;
        }
        uint64 subset = tdbVmapNew();
        for (uint64 i = 0 ; i < data_providers_num ; i++) {
            string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
            uint64 rows = tdbGetRowCount(datasource, table);
            pd_shared3p float64[[1]] best_attribute_column(rows);
            pd_shared3p int64[[1]] example_indexes = tdbVmapGetValue(example_indexes_vmap, "0", i :: uint64);
            for (uint64 j = 0; j < columns; j++) {
                pd_shared3p bool eq = (j == best_attribute_original_index);
                best_attribute_column += (float64)eq * tdbReadColumn(datasource, table, j);
            }
            pd_shared3p int64[[1]] partial_subset(rows) = (int64)(best_attribute_column == value) * (int64)(example_indexes != 0);
            tdbVmapAddValue(subset, "0", partial_subset);
        }
        pd_shared3p xor_uint8[[1]] branch = bl_strCat(quote, itoa(best_attribute));
        branch = bl_strCat(branch, eq_str);
        branch = bl_strCat(branch, itoa((int64)value));
        branch = bl_strCat(branch, quote);
        branch = bl_strCat(branch, colon);

        if (declassify(sum(subset, data_providers_num) == 0)) {
            branch = bl_strCat(branch, itoa(most_common_label(example_indexes_vmap)));
        } else {
            uint64[[1]] attribute_indexes = iota(size(attributes));
            pd_shared3p int64[[1]] lt = (int64)(attribute_indexes < best_attribute_index);
            pd_shared3p int64[[1]] gt = (int64)(attribute_indexes > best_attribute_index);
            pd_shared3p int64[[1]] first_half(size(attributes)) = lt * (int64)attributes + (1-lt) * (-1);
            pd_shared3p int64[[1]] second_half(size(attributes)) = gt * (int64)attributes + (1-gt) * (-1);
            pd_shared3p int64[[1]] new_attribs(size(attributes)-1) = first_half[:size(attributes)-1];
            for (uint64 i = size(attributes)-1; i > 0; i--) {
                pd_shared3p bool neq = (second_half[i] != -1);
                new_attribs[i-1] += (int64)neq * (1+second_half[i]);
            }
            branch = bl_strCat(branch, id3(subset, (uint64)new_attribs));
        }
        branches = bl_strCat(branches, branch);
        if (v < max_attribute_values) {
            branches = bl_strCat(branches, comma);
        }
        branches = bl_strCat(branches, space);
    }

    pd_shared3p xor_uint8[[1]] root = bl_strCat(left_curly_br, branches);
    return bl_strCat(root, right_curly_br);
}

uint64 providers_vmap;
uint64 data_providers_num;
uint64 max_attribute_values;
uint64 class_index;

pd_shared3p uint64[[1]] original_attributes;
pd_shared3p float64[[2]] possible_values;

uint64 rows;
uint64 columns;

pd_shared3p xor_uint8[[1]] quote;
pd_shared3p xor_uint8[[1]] comma;
pd_shared3p xor_uint8[[1]] eq_str;
pd_shared3p xor_uint8[[1]] space;
pd_shared3p xor_uint8[[1]] colon;
pd_shared3p xor_uint8[[1]] left_curly_br;
pd_shared3p xor_uint8[[1]] right_curly_br;

// sed 's/, }/ }/g' id3.out to remove some extra commas