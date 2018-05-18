import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

import shared3p_table_database;
import table_database;
// import data_input;

/**
 * private arr: 1D array of all data. size M, where M: #attributes
 * public cells: number of the histogram's cell
 * private min: min value of arr
 * private max: max value of arr
**/
template <domain D, type T>
D uint64[[1]] histogram(D T[[1]] arr, uint64 cells, D T min, D T max) {
    D uint64[[1]] output(cells);
    D float64 cell_width = ((float64) max - (float64) min) / (float64)cells;
    D uint64[[1]] cellmap = (uint64)((float64)(arr-min)/cell_width);
    for (uint64 j = 0; j < cells; j++) {
        D uint64[[1]] eq = (uint64)(cellmap == j) + ((uint64)(cellmap == cells) * (uint64)(j == cells-1));
        output[j] = sum(eq);
    }
    return output;
}

/**
 * public string datasource: name of the datasource
 * public string table: name of the table
 * public uint64 index: column index in the table
 * public cells: number of the histogram's cell
 * private min: min value of arr
 * private max: max value of arr
**/
template <domain D, type T>
D uint64[[1]] histogram(string datasource, string table, uint64 index, uint64 cells, D T min, D T max) {
    D T[[1]] column = tdbReadColumn(datasource, table, index);
    return(histogram(column, cells, min, max));
}

/**
 * public string datasource: name of the datasource
 * public uint64 providers_vmap: A tdb-Vmap with key 0 and value an array of the data-provider names
 * public uint64 data_providers_num: the number of data-providers
 * public uint64 index: column index in the table
 * public cells: number of the histogram's cell
 * private min: min value of arr
 * private max: max value of arr
**/
template <domain D, type T>
D uint64[[1]] histogram(string datasource, uint64 providers_vmap, uint64 data_providers_num, uint64 index, uint64 cells, D T min, D T max) {
    D uint64[[1]] result(cells);
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        print("Computing aggregates for data-provider " + table);
        D T[[1]] column = tdbReadColumn(datasource, table, index);
        result += histogram(column, cells, min, max);
    }
    return result;
}


/**
 * private arr: 1D array of all data. size M, where M: #attributes
 * public int P: the number of different possible values contained in arr
**/
template <domain D, type T>
D uint64[[1]] histogram_categorical(D T[[1]] arr, uint64 P) {
    D uint64[[1]] output(P);
    for (uint64 i = 0; i < P; i++) {
        D uint64[[1]] eq = (uint64)((uint64)arr == i);
        output[i] = sum(eq);
    }
    return output;
}

/**
 * public string datasource: name of the datasource
 * public string table: name of the table
 * public uint64 index: column index in the table
 * public int P: the number of different possible values contained in arr
**/
template <domain D, type T>
D uint64[[1]] histogram_categorical(string datasource, string table, uint64 index, uint64 P) {
    D T[[1]] column = tdbReadColumn(datasource, table, index);
    return(histogram_categorical(column, P));
}

/**
 * public string datasource: name of the datasource
 * public uint64 providers_vmap: A tdb-Vmap with key 0 and value an array of the data-provider names
 * public uint64 data_providers_num: the number of data-providers
 * public uint64 index: column index in the table
 * public int P: the number of different possible values contained in arr
**/
template <domain D, type T>
D uint64[[1]] histogram_categorical(string datasource, uint64 providers_vmap, uint64 data_providers_num, uint64 index, uint64 P) {
    D uint64[[1]] result(P);
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        print("Computing aggregates for data-provider " + table);
        D T[[1]] column = tdbReadColumn(datasource, table, index);
        result += histogram_categorical(column, P);
    }
    return result;
}


/**
 * private arr: 2D array of all data tuples. size M x N, where M: #attributes, N: #tuples
 * public cells_list: list of numbers of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
**/
template <domain D, type T>
D uint64[[1]] histogram(D T[[2]] arr, uint64[[1]] cells_list, D T[[1]] mins, D T[[1]] maxs) {
    uint64[[1]] array_shape = shape(arr);
    uint64 dims = array_shape[0];
    uint64 individuals = array_shape[1];
    uint64 len = product(cells_list);
    D uint64[[1]] hist_1d(len);
    D float64[[1]] cell_widths(dims) = (((float64) maxs - (float64) mins) / (float64)cells_list);
    for (uint64 j = 0; j < individuals; j++) {
        D uint64 pos = 0;
        for (uint64 i = 0; i < dims; i++) {
            uint64 prod = product(cells_list[i+1:]);
            D uint64 cell = (uint64)((float64)(arr[i,j] - (float64)mins[i]) / (float64)cell_widths[i]);
            cell -= (uint64)(cell == cells_list[i]);
            pos += cell * prod;
        }
        for (uint64 i = 0; i < len; i++) {
            D uint64 eq = (uint64)(pos == i);
            hist_1d[i] += eq;
        }
    }
    return hist_1d;
}

/**
 * private arr: 2D array of all data tuples. size N x M, where N: #tuples, M: #attributes
 * public number_of_histograms: the number of histograms to be computed
 * public attributes: attributes of arr, for which we compute their histograms (column indexes of arr)
 * public cells_list: list of numbers of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
**/
template <domain D>
uint64 multiple_histograms(D float64[[2]] arr, uint64 number_of_histograms, uint64 attributes_vmap, uint64 cells_vmap, D float64[[1]] mins, D float64[[1]] maxs) {
    uint64 histograms = tdbVmapNew();                                           // map of all histograms to compute; histograms[0] contains histogram 0, etc
    uint64 N = shape(arr)[0];                                                  // number of tuples
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        D uint64[[1]] positions(N);
        uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
        uint64 requested_attributes = size(cells);                                 // amount of attributes wanted for this histogram
        for (uint64 a = 0; a < requested_attributes; a++) {                        // for each attribute
            uint64 number_of_cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64)[a];
            uint64 attribute = tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a];
            D float64 max = maxs[attribute];
            D float64 min = mins[attribute];
            D float64 width = (((float64) (max - min)) / (float64) number_of_cells);
            D uint64[[1]] cellmap = (uint64) ((float64) (arr[:,attribute] - mins[attribute]) / width);
            cellmap -= (uint64)(cellmap == cells[a]);
            uint64 prod = product(cells[a+1:]);
            positions += cellmap * prod;
        }
        uint64 length = product(cells);
        D uint64[[1]] histogram(length);
        for (uint64 j = 0; j < length ; j++) {                      // for each cell of histogram h
            D bool[[1]] eq = (positions == j);
            histogram[j] = sum(eq);
        }
        tdbVmapAddValue(histograms, arrayToString(h), histogram);
    }
    return histograms;
}

/**
 * private arr: 2D array of all data tuples. size N x M, where N: #tuples, M: #attributes
 * public number_of_histograms: the number of histograms to be computed
 * public attributes: attributes of arr, for which we compute their histograms (column indexes of arr)
 * public cells_list: list of numbers of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
 * public bool_op: boolean operator appllied between all constraints
 * public constraint_attributes: list of attributes to filter
 * public constraint_operators: list of operators to be used in the filtering
 * public constraint_values: list of values to be used in the filtering
**/
template <domain D>
uint64 multiple_histograms(D float64[[2]] arr, uint64 number_of_histograms, uint64 attributes_vmap, uint64 cells_vmap, D float64[[1]] mins, D float64[[1]] maxs, string bool_op, uint64[[1]] constraint_attributes, uint64[[1]] constraint_operators, float64[[1]] constraint_values) {
    uint64 histograms = tdbVmapNew();                                           // map of all histograms to compute; histograms[0] contains histogram 0, etc
    uint64 N = shape(arr)[0];                                                  // number of tuples
    D uint64[[1]] constraint_map(N) = constraint_map(arr, bool_op,  constraint_attributes, constraint_operators, constraint_values);
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        D uint64[[1]] positions(N);
        uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
        uint64 requested_attributes = size(cells);                                 // amount of attributes wanted for this histogram
        for (uint64 a = 0; a < requested_attributes; a++) {                        // for each attribute
            uint64 number_of_cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64)[a];
            uint64 attribute = tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a];
            D float64 max = maxs[attribute];
            D float64 min = mins[attribute];
            D float64 width = (((float64) (max - min)) / (float64) number_of_cells);
            D uint64[[1]] cellmap = (uint64) ((float64) (arr[:,attribute] - mins[attribute]) / width);
            cellmap -= (uint64)(cellmap == cells[a]);
            uint64 prod = product(cells[a+1:]);
            positions += cellmap * prod;
        }
        uint64 length = product(cells);
        D uint64[[1]] histogram(length);
        for (uint64 j = 0; j < length ; j++) {                      // for each cell of histogram h
            D bool[[1]] eq = (bool)((uint64)(positions == j) * constraint_map);
            histogram[j] = sum(eq);
        }
        tdbVmapAddValue(histograms, arrayToString(h), histogram);
    }
    return histograms;
}

/**
 * public datasource: name of the datasource
 * public table: name of the table
 * public number_of_histograms: the number of histograms to be computed
 * public attributes_vmap: list(vmap) of attributes of the table, for which we compute their histograms (column indexes)
 * public cells_vmap: list(vmap) of numbers of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
**/
template <domain D>
uint64 multiple_histograms(string datasource, string table, uint64 number_of_histograms, uint64 attributes_vmap, uint64 cells_vmap, D float64[[1]] mins, D float64[[1]] maxs) {
    uint64 histograms = tdbVmapNew();                                           // map of all histograms to compute; histograms[0] contains histogram 0, etc
    uint64 N = tdbGetRowCount(datasource, table);                               // number of tuples
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        D uint64[[1]] positions(N);
        uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
        uint64 requested_attributes = size(cells);                                 // amount of attributes wanted for this histogram
        for (uint64 a = 0; a < requested_attributes; a++) {                        // for each attribute
            uint64 number_of_cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64)[a];
            uint64 attribute = tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a];
            D float64 max = maxs[attribute];
            D float64 min = mins[attribute];
            D float64 width = (((float64) (max - min)) / (float64) number_of_cells);
            D float64[[1]] column = tdbReadColumn(datasource, table, attribute);
            D uint64[[1]] cellmap = (uint64) ((float64) (column - min) / width);
            cellmap -= (uint64)(cellmap == cells[a]);
            uint64 prod = product(cells[a+1:]);
            positions += cellmap * prod;
        }
        uint64 length = product(cells);
        D uint64[[1]] histogram(length);
        for (uint64 j = 0; j < length ; j++) {                      // for each cell of histogram h
            D bool[[1]] eq = (positions == j);
            histogram[j] = sum(eq);
        }
        tdbVmapAddValue(histograms, arrayToString(h), histogram);
    }
    return histograms;
}

/**
 * public datasource: name of the datasource
 * public table: name of the table
 * public number_of_histograms: the number of histograms to be computed
 * public attributes_vmap: attributes of the table, for which we compute their histograms (column indexes)
 * public cells_vmap: list of numbers of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
 * public bool_op: boolean operator appllied between all constraints
 * public constraint_attributes: list of attributes to filter
 * public constraint_operators: list of operators to be used in the filtering
 * public constraint_values: list of values to be used in the filtering
**/
template <domain D>
uint64 multiple_histograms(string datasource, string table, uint64 number_of_histograms, uint64 attributes_vmap, uint64 cells_vmap, D float64[[1]] mins, D float64[[1]] maxs, string bool_op, uint64[[1]] constraint_attributes, uint64[[1]] constraint_operators, float64[[1]] constraint_values) {
    uint64 histograms = tdbVmapNew();                                           // map of all histograms to compute; histograms[0] contains histogram 0, etc
    uint64 N = tdbGetRowCount(datasource, table);                               // number of tuples
    D uint64[[1]] constraint_map(N) = constraint_map(datasource, table, bool_op,  constraint_attributes, constraint_operators, constraint_values);
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        D uint64[[1]] positions(N);
        uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
        uint64 requested_attributes = size(cells);                                 // amount of attributes wanted for this histogram

        for (uint64 a = 0; a < requested_attributes; a++) {                        // for each attribute
            uint64 number_of_cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64)[a];
            uint64 attribute = tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a];
            D float64 max = maxs[attribute];
            D float64 min = mins[attribute];
            D float64 width = (((float64) (max - min)) / (float64) number_of_cells);
            D float64[[1]] column = tdbReadColumn(datasource, table, attribute);
            D uint64[[1]] cellmap = (uint64) ((float64) (column - min) / width);

            cellmap -= (uint64)(cellmap == cells[a]);
            uint64 prod = product(cells[a+1:]);
            positions += cellmap * prod;
        }
        uint64 length = product(cells);
        D uint64[[1]] histogram(length);
        for (uint64 j = 0; j < length ; j++) {                      // for each cell of histogram h
            D bool[[1]] eq = (bool)((uint64)(positions == j) * constraint_map);
            histogram[j] = sum(eq);
        }
        tdbVmapAddValue(histograms, arrayToString(h), histogram);
    }
    return histograms;
}

/**
 * public datasource: name of the datasource
 * public uint64 providers_vmap: A tdb-Vmap with key 0 and value an array of the data-provider names
 * public uint64 data_providers_num: the number of data-providers
 * public number_of_histograms: the number of histograms to be computed
 * public attributes_vmap: list(vmap) of attributes of the table, for which we compute their histograms (column indexes)
 * public cells_vmap: list(vmap) of numbers of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
**/
template <domain D>
uint64 multiple_histograms(string datasource, uint64 providers_vmap, uint64 data_providers_num, uint64 number_of_histograms, uint64 attributes_vmap, uint64 cells_vmap, D float64[[1]] mins, D float64[[1]] maxs) {
    uint64[[1]] results(data_providers_num);
    for (uint64 j = 0 ; j < data_providers_num ; j++) {
        string table = tdbVmapGetString(providers_vmap, "0", j);
        print("Computing aggregates for data-provider " + table);
        uint64 res = multiple_histograms(datasource, table, number_of_histograms, attributes_vmap, cells_vmap, mins, maxs);
        results[j] = res;
    }
    uint64 histograms = tdbVmapNew();

    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        pd_shared3p uint64[[1]] hist = tdbVmapGetValue( results[0], arrayToString(h), 0 :: uint64);
        for (uint64 j = 1 ; j < data_providers_num ; j++) {
            pd_shared3p uint64[[1]] res_hist = tdbVmapGetValue(results[j], arrayToString(h), 0 :: uint64);
            hist += res_hist;
        }
        tdbVmapAddValue(histograms, arrayToString(h), hist);
    }
    return histograms;
}


/**
 * public datasource: name of the datasource
 * public uint64 providers_vmap: A tdb-Vmap with key 0 and value an array of the data-provider names
 * public uint64 data_providers_num: the number of data-providers
 * public number_of_histograms: the number of histograms to be computed
 * public attributes_vmap: attributes of the table, for which we compute their histograms (column indexes)
 * public cells_vmap: list of numbers of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
 * public bool_op: boolean operator appllied between all constraints
 * public constraint_attributes: list of attributes to filter
 * public constraint_operators: list of operators to be used in the filtering
 * public constraint_values: list of values to be used in the filtering
**/
template <domain D>
uint64 multiple_histograms(string datasource, uint64 providers_vmap, uint64 data_providers_num, uint64 number_of_histograms, uint64 attributes_vmap, uint64 cells_vmap, D float64[[1]] mins, D float64[[1]] maxs, string bool_op, uint64[[1]] constraint_attributes, uint64[[1]] constraint_operators, float64[[1]] constraint_values) {
    uint64[[1]] results(data_providers_num);
    for (uint64 j = 0 ; j < data_providers_num ; j++) {
        string table = tdbVmapGetString(providers_vmap, "0", j);
        print("Computing aggregates for data-provider " + table);
        uint64 res = multiple_histograms(datasource, table, number_of_histograms, attributes_vmap, cells_vmap, mins, maxs, bool_op, constraint_attributes, constraint_operators, constraint_values);
        results[j] = res;
    }
    uint64 histograms = tdbVmapNew();

    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        pd_shared3p uint64[[1]] hist = tdbVmapGetValue( results[0], arrayToString(h), 0 :: uint64);
        for (uint64 j = 1 ; j < data_providers_num ; j++) {
            pd_shared3p uint64[[1]] res_hist = tdbVmapGetValue(results[j], arrayToString(h), 0 :: uint64);
            hist += res_hist;
        }
        tdbVmapAddValue(histograms, arrayToString(h), hist);
    }
    return histograms;
}

template<domain D>
D uint64[[1]] constraint_map(string datasource, string table, string bool_op, uint64[[1]] constraint_attributes, uint64[[1]] constraint_operators, float64[[1]] constraint_values){
    uint64 N = tdbGetRowCount(datasource, table);                               // number of tuples
    D uint64[[1]] constraint_map(N);
    if (bool_op == "AND"){
        constraint_map = 1;
    } else if(bool_op == "OR") {
        constraint_map = 0;
    } else if(bool_op == "XOR") {
        constraint_map = 0;
    }
    for (uint c = 0; c < size(constraint_attributes); c++) {
        pd_shared3p float64[[1]] constraint_attribute = tdbReadColumn(datasource, table, constraint_attributes[c]);
        pd_shared3p float64 constraint_value = constraint_values[c];
        pd_shared3p uint64[[1]] eq;
        if (constraint_operators[c] == 0) {
            eq = (uint64)(constraint_attribute > constraint_value);
        } else if (constraint_operators[c] == 1) {
            eq = (uint64)(constraint_attribute < constraint_value);
        } else if (constraint_operators[c] == 2) {
            eq = (uint64)(constraint_attribute == constraint_value);
        }
        if (bool_op == "AND"){
            constraint_map *= eq;
        } else if(bool_op == "OR") {
            constraint_map += eq;
        } else if(bool_op == "XOR") {
            constraint_map = constraint_map * (1 - eq) + (1 - constraint_map) * eq;
        }
    }
    return constraint_map;
}

template<domain D>
D uint64[[1]] constraint_map(D float64[[2]] arr, string bool_op, uint64[[1]] constraint_attributes, uint64[[1]] constraint_operators, float64[[1]] constraint_values){
    uint64[[1]] array_shape = shape(arr);
    uint64 N = array_shape[0];                              // number of tuples
    D uint64[[1]] constraint_map(N);
    if (bool_op == "AND"){
        constraint_map = 1;
    } else if(bool_op == "OR") {
        constraint_map = 0;
    } else if(bool_op == "XOR") {
        constraint_map = 0;
    }
    for (uint c = 0; c < size(constraint_attributes); c++) {
        uint64 constraint_attribute_index = constraint_attributes[c];
        pd_shared3p float64[[1]] constraint_attribute = arr[:,constraint_attribute_index];
        pd_shared3p float64 constraint_value = constraint_values[c];
        pd_shared3p uint64[[1]] eq;
        if (constraint_operators[c] == 0) {
            eq = (uint64)(constraint_attribute > constraint_value);
        } else if (constraint_operators[c] == 1) {
            eq = (uint64)(constraint_attribute < constraint_value);
        } else if (constraint_operators[c] == 2) {
            eq = (uint64)(constraint_attribute == constraint_value);
        }
        if (bool_op == "AND"){
            constraint_map *= eq;
        } else if(bool_op == "OR") {
            constraint_map += eq;
        } else if(bool_op == "XOR") {
            constraint_map = constraint_map * (1 - eq) + (1 - constraint_map) * eq;
        }
    }
    return constraint_map;
}



/* Test Histogram */
// void main() {
//     /* Test 1d histogram with floats */
//     uint64 cells = 3;
//     pd_shared3p float64[[1]] data_float = {0,1,2,3,4,5,6,7,8,9};
//     pd_shared3p float64 min_float = min(data_float), max_float = max(data_float);
//     pd_shared3p uint64[[1]] hist_float = histogram(data_float, cells, min_float, max_float);
//     print("{",1,", ",cells,"} Histogram");
//     print(arrayToString(declassify(hist_float)));
//     print("\n");
//
//
//     /* Test 1d histogram with integers */
//     pd_shared3p uint64[[1]] data_int = {0,1,2,3,4,5,6,7,8};
//     pd_shared3p uint64 min_int = min(data_int), max_int = max(data_int);
//     pd_shared3p uint64[[1]] hist_int = histogram(data_int, cells, min_int, max_int);
//     print("{",1,", ",cells,"} Histogram");
//     print(arrayToString(declassify(hist_int)));
//     print("\n");
//
//
//     /* Test multi-dimensional histogram with floats */
//     pd_shared3p float64[[2]] data = reshape({0,1,2,3,4,5,6,7,8,9,
//                                             0,1,2,3,4,5,6,7,8,9}, 2, 10);
//     uint64[[1]] cells_list = {3,3};
//     pd_shared3p float64[[1]] mins = {0,0};
//     pd_shared3p float64[[1]] maxs = {9,9};
//     print(arrayToString(cells_list), " Histogram");
//     printVector(declassify(histogram(data, cells_list, mins, maxs)));
//     print("\n");
//
//
//     /* Test multiple_histograms with floats */
//     pd_shared3p float64[[2]] data2 = reshape({1,2,3,4,
//                                             1,3,5,2,
//                                             2,4,3,2,
//                                             7,6,4,1,
//                                             6,3,2,2,
//                                             6,2,5,3}, 6, 4);
//     pd_shared3p float64[[1]] mins2 = {1,2,2,1};
//     pd_shared3p float64[[1]] maxs2 = {7,6,5,4};
//
//     uint64 attributes_vmap = tdbVmapNew();
//     uint64[[1]] value = {1,2,3};
//     tdbVmapAddValue(attributes_vmap, "0", value);
//     value = {1,2};
//     tdbVmapAddValue(attributes_vmap, "1", value);
//     value = {2,3};
//     tdbVmapAddValue(attributes_vmap, "2", value);
//
//     uint64 cells_vmap = tdbVmapNew();
//     value = {3,3,3};
//     tdbVmapAddValue(cells_vmap, "0", value);
//     value = {3,3};
//     tdbVmapAddValue(cells_vmap, "1", value);
//     value = {3,3};
//     tdbVmapAddValue(cells_vmap, "2", value);
//
//     uint64 histograms = multiple_histograms(data2, 3::uint64, attributes_vmap, cells_vmap, mins2, maxs2);
//
//     pd_shared3p uint64[[1]] res = tdbVmapGetValue(histograms, "0", 0 :: uint64);
//     uint64[[1]] cells_res = tdbVmapGetValue(cells_vmap, "0", 0 :: uint64);
//     print(arrayToString(cells_res), " Histogram");
//     printVector(declassify(res));
//     print("\n");
//     res = tdbVmapGetValue(histograms, "1", 0 :: uint64);
//     cells_res = tdbVmapGetValue(cells_vmap, "1", 0 :: uint64);
//     print(arrayToString(cells_res), " Histogram");
//     printVector(declassify(res));
//     print("\n");
//     res = tdbVmapGetValue(histograms, "2", 0 :: uint64);
//     cells_res = tdbVmapGetValue(cells_vmap, "2", 0 :: uint64);
//     print(arrayToString(cells_res), " Histogram");
//     printVector(declassify(res));
//     print("\n");
//
//     /* Test multiple_histograms with imported data */
//     uint64 attributes_vmap2 = tdbVmapNew();
//     uint64[[1]] value2 = {11,12};
//     tdbVmapAddValue(attributes_vmap2, "0", value2);
//
//     uint64 cells_vmap2 = tdbVmapNew();
//     value2 = {3,5};
//     tdbVmapAddValue(cells_vmap2, "0", value2);
//
//     print("Computing histograms");
//     uint64 histograms2 = multiple_histograms(imported_array, 1::uint64, attributes_vmap2, cells_vmap2, imported_mins, imported_maxs);
//     pd_shared3p uint64[[1]] res1 = tdbVmapGetValue(histograms2, "0", 0 :: uint64);
//     uint64[[1]] cells_res1 = tdbVmapGetValue(cells_vmap2, "0", 0 :: uint64);
//     print(arrayToString(cells_res1), " Histogram");
//     printVector(declassify(res1));
//     print("\n");
//
//
//     string datasource = "DS1"; // Data source name
//     string tbl = "centricity_identified-100_edited"; // Table name
//
//     /* Test multiple_histograms with imported data */
//     uint64 attributes_vmap3 = tdbVmapNew();
//     uint64[[1]] value3 = {11,12};
//     tdbVmapAddValue(attributes_vmap3, "0", value3);
//
//     uint64 cells_vmap3 = tdbVmapNew();
//     value3 = {3,5};
//     tdbVmapAddValue(cells_vmap3, "0", value3);
//
//     // Open database before running operations on it
//     tdbOpenConnection(datasource);
//     print("Computing mins, maxs");
//     uint64 column_count = tdbGetColumnCount(datasource, tbl);
//     pd_shared3p float64[[1]] mins4(column_count);
//     pd_shared3p float64[[1]] maxs4(column_count);
//     for (uint64 j = 0; j < column_count; j++ ) {
//       pd_shared3p float64[[1]] column = tdbReadColumn(datasource, tbl, j);
//       mins4[j] = min(column);
//       maxs4[j] = max(column);
//     }
//
//     print("Computing histograms");
//     uint64 histograms3 = multiple_histograms(datasource, tbl, 1::uint64, attributes_vmap3, cells_vmap3, mins4, maxs4);
//     pd_shared3p uint64[[1]] res2 = tdbVmapGetValue(histograms3, "0", 0 :: uint64);
//     uint64[[1]] cells_res2 = tdbVmapGetValue(cells_vmap3, "0", 0 :: uint64);
//     print(arrayToString(cells_res2), " Histogram");
//     printVector(declassify(res2));
//     print("\n");
//
//     /* Test multiple_histograms with imported data along with constraints*/
//
//     uint64 attributes_vmap4 = tdbVmapNew();
//     uint64[[1]] value4 = {13, 14};
//     tdbVmapAddValue(attributes_vmap4, "0", value4);
//
//     uint64 cells_vmap4 = tdbVmapNew();
//     value4 = {3,5};
//     tdbVmapAddValue(cells_vmap4, "0", value4);
//
//     string bool_op = "AND"; // 0:"AND" 1:"OR" 2:"XOR"
//
//     uint64[[1]] constraint_attributes = {25, 25, 26, 26};
//     uint64[[1]] constraint_operators = {0, 1, 0, 1}; //0:">" 1:"<" 2:"=="
//     float64[[1]] constraint_values = {95.85, 105.35, 59.46, 61.55};
//
//     uint64 histograms4 = multiple_histograms(datasource, tbl, 2::uint64, attributes_vmap4, cells_vmap4, mins4, maxs4, bool_op, constraint_attributes, constraint_operators, constraint_values);
//     pd_shared3p uint64[[1]] res3 = tdbVmapGetValue(histograms4, "0", 0 :: uint64);
//     uint64[[1]] cells_res3 = tdbVmapGetValue(cells_vmap4, "0", 0 :: uint64);
//     print(arrayToString(cells_res3), " Histogram");
//     printVector(declassify(res3));
//     print("\n");
//
//     /* Test multiple_histograms with imported data along with constraints from multiple providers*/
//     string datasource = "DS1";
//     uint64 data_providers_num = 3;
//     string table_1 = "data_provider_1";
//     string table_2 = "data_provider_2";
//     string table_3 = "data_provider_3";
//
//     // Create the data-providers list
//     uint64 providers_vmap = tdbVmapNew();
//     tdbVmapAddString(providers_vmap, "0", table_1);
//     tdbVmapAddString(providers_vmap, "0", table_2);
//     tdbVmapAddString(providers_vmap, "0", table_3);
//
//     ///////////////////////////////
//     print("Opening connection to db: ", datasource);
//     tdbOpenConnection(datasource);
//     for (uint64 i = 0 ; i < data_providers_num ; i++) {
//         string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
//         print("Table: " + table);
//
//         // pd_shared3p uint64 data_type;
//         // Check if a table exists
//         if (tdbTableExists(datasource, table)) {
//           // Delete existing table
//           print("Deleting existing table: ", table);
//           tdbTableDelete(datasource, table);
//         }
//
//         print("Creating new table: ", table);
//
//         uint64 nrows = shape(imported_array)[0];
//         uint64 ncols = shape(imported_array)[1];;
//         pd_shared3p float64 vtype;
//         tdbTableCreate(datasource, table, vtype, ncols);
//
//         print("Inserting data to table " + table + "...");
//         pd_shared3p float64[[1]] row;
//         for (uint i = 0; i < nrows; ++i) {
//             row = imported_array[i,:];
//             tdbInsertRow(datasource, table, row);
//         }
//         print("Done inserting in table " + table + "\n\n");
//     }
//     print("Done inserting!");
//     ///////////////////////////////
//
//     uint64 histograms5 = multiple_histograms(datasource, providers_vmap, data_providers_num, 1::uint64, attributes_vmap4, cells_vmap4, imported_mins, imported_maxs, bool_op, constraint_attributes, constraint_operators, constraint_values);
//     pd_shared3p uint64[[1]] res4 = tdbVmapGetValue(histograms5, "0", 0 :: uint64);
//     uint64[[1]] cells_res4 = tdbVmapGetValue(cells_vmap4, "0", 0 :: uint64);
//     print(arrayToString(cells_res4), " Histogram");
//     printVector(declassify(res4));
//     print("\n");
//
//
//
//     tdbCloseConnection(datasource);
// }
