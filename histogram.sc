import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

import shared3p_table_database;
import table_database;

template <domain D, type T>
D uint64[[1]] histogram(D T[[1]] arr, uint64 cells, D T min, D T max){
    D uint64[[1]] output(cells);
    D uint64 cell_width = (uint64) ceiling((float64)(max+1 - min) / (float64)cells);
    uint64 len = size(arr);
    for (uint64 i = 0; i < len; i++) {
        D uint64 cell = (uint64)(arr[i] / (T)cell_width);
        for (uint64 j = 0; j < cells; j++) {
            D bool eq = (cell == j);
            output[j] += (uint64)eq;
        }
    }
    return output;
}

template <domain D, type T>
D uint64[[2]] histogram(D T[[1]] arr1, D T[[1]] arr2, uint64 cells1, uint64 cells2, D T min1, D T max1, D T min2, D T max2){
    D uint64[[2]] output(cells1, cells2);
    D uint64 cell_width1 = (uint64) ceiling((max1+1 - min1) / (float64)cells1);
    D uint64 cell_width2 = (uint64) ceiling((max2+1 - min2) / (float64)cells2);
    uint64 len = size(arr1);
    for (uint64 k = 0; k < len; k++) {
        D uint64 cell1 = (uint64)(arr1[k] / (T)cell_width1);
        D uint64 cell2 = (uint64)(arr2[k] / (T)cell_width2);
        for (uint64 i = 0; i < cells1; i++) {
            for (uint64 j = 0; j < cells2; j++) {
                D bool eq1 = (cell1 == i);
                D bool eq2 = (cell2 == j);
                output[i,j] += (uint64)(eq1) * (uint64)(eq2);
            }
        }
    }
    return output;
}

//TODO: extensive testing multiD, templates, dimensions
// template<dim N>
pd_shared3p uint64[[1]] histogram(pd_shared3p float64[[2]] arr, uint64[[1]] cells, pd_shared3p float64[[1]] mins, pd_shared3p float64[[1]] maxs){
    uint64[[1]] array_shape = shape(arr);
    uint64 dims = array_shape[0];
    uint64 individuals = array_shape[1];
    uint64 len = product(cells);
    pd_shared3p uint64[[1]] hist_1d(len);
    pd_shared3p uint64[[1]] cell_widths(dims) = (uint64)ceiling((maxs+1 - mins) / (float64)cells);
    for(uint64 j = 0; j < individuals; j++){
        pd_shared3p uint64[[1]] positions(dims);
        for(uint64 i = 0; i < dims; i++){
            positions[i] = (uint64)(arr[i,j] / (float64)cell_widths[i]);
        }
        pd_shared3p uint64 pos = 0;
        for(uint64 i = 0; i < dims; i++){
            uint64 prod = product(cells[i+1:]);
            pos += positions[i] * prod;
        }
        for(uint64 i = 0; i < len; i++){
            pd_shared3p bool eq = (pos == i);
            hist_1d[i] += (uint64)eq;
        }
    }
    return hist_1d;
}


/**
 * private arr: 2D array of all data tuples. size N x M, where N: #tuples, M: #attributes
 * public attributes: attributes of arr, for which we compute their histograms (column indexes of arr)
 * public cells_list: list of number of cells for each histogram
 * private mins: list of min values for each attribute
 * private maxs: list of max values for each attribute
**/
template <domain D>
uint64 multiple_1d_histograms(D float64[[2]] arr, uint64[[1]] attributes, uint64[[1]] cells_list, D float64[[1]] mins, D float64[[1]] maxs) {
    uint64 histograms = tdbVmapNew(); // map of all histograms to compute; histograms[0] contains histogram 0, etc
    uint64 number_of_histograms = size(attributes);                             // = size(cells_list);
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // initialize each histogram
        D uint64[[1]] histogram(cells_list[h]);
        tdbVmapAddValue(histograms, arrayToString(h), histogram);
    }

    // compute cell widths for each histogram
    D uint64[[1]] cell_widths(number_of_histograms);                            // list of cell-widths for each histogram
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        uint64 number_of_cells = cells_list[h];
        D float64 max = maxs[attributes[h]];
        D float64 min = mins[attributes[h]];
        cell_widths[h] = (uint64) ceiling((max+1 - min) / (float64)number_of_cells);
    }

    uint64[[1]] array_shape = shape(arr);
    uint64 N = array_shape[0];                                                  // number of tuples
    for (uint64 t = 0; t < N; t++) {                                            // for each tuple
        for (uint64 h = 0; h < number_of_histograms; h++) {                     // for each histogram
            uint64 a = attributes[h];
            D float64 value = arr[t, a];                                        // value for column attributes[h] of tuple t

            D uint64 cell = (uint64)(value / (float64)cell_widths[h]);          // histogram cell that value belongs
            D uint64[[1]] histogram = tdbVmapGetValue(histograms, arrayToString(h), 0 :: uint64);
            tdbVmapErase(histograms, arrayToString(h));
            for (uint64 j = 0; j < cells_list[h]; j++) {                        // for each cell of histogram h
                D bool eq = (cell == j);
                histogram[j] += (uint64)eq;
            }
            tdbVmapAddValue(histograms, arrayToString(h), histogram);
        }

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
**/
template <domain D>
uint64 multiple_histograms(D float64[[2]] arr, uint64 number_of_histograms, uint64 attributes_vmap, uint64 cells_vmap, D float64[[1]] mins, D float64[[1]] maxs) {
    uint64 histograms = tdbVmapNew();                                           // map of all histograms to compute; histograms[0] contains histogram 0, etc
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // initialize each histogram
        uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
        uint64 length = product(cells);
        D uint64[[1]] histogram(length);
        tdbVmapAddValue(histograms, arrayToString(h), histogram);
    }

    // compute cell widths for each histogram
    uint64 cell_widths = tdbVmapNew();                                          // map of cell-widths for each histogram
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
        uint64 wanted_attributes = size(cells);                                 // amount of attributes wanted for this histogram
        D uint64[[1]] widths(wanted_attributes);                                // widths for each cell of histogram h
        for (uint64 a = 0; a < wanted_attributes; a++) {                        // for each attribute
            uint64 number_of_cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64)[a];
            D float64 max = maxs[tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a]];
            D float64 min = mins[tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a]];
            widths[a] = (uint64) ceiling((max+1 - min) / (float64)number_of_cells);
        }
        tdbVmapAddValue(cell_widths, arrayToString(h), widths);
    }

    uint64[[1]] array_shape = shape(arr);
    uint64 N = array_shape[0];                                                  // number of tuples
    for (uint64 t = 0; t < N; t++) {                                            // for each tuple
        for (uint64 h = 0; h < number_of_histograms; h++) {                     // for each histogram
            uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
            uint64 wanted_attributes = size(cells);                             // amount of attributes wanted for this histogram
            D uint64[[1]] positions(wanted_attributes);                         // multiple indexes as we had a multi-dimensional array

            D uint64[[1]] widths = tdbVmapGetValue(cell_widths, arrayToString(h), 0 :: uint64);

            for (uint64 a = 0; a < wanted_attributes; a++) {                    // for each attribute
                uint64 attribute = tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a];
                D float64 value = arr[t, attribute];                            // value for column attributes[h] of tuple t

                D uint64 cell = (uint64)(value / (float64)widths[a]);           // histogram cell that value belongs
                positions[a] = cell;
            }

            D uint64 pos = 0;                                                   // compute 1-d index from multiple indexes
            for(uint64 i = 0; i < wanted_attributes; i++){
                uint64 prod = product(cells[i+1:]);
                pos += positions[i] * prod;
            }
            D uint64[[1]] histogram = tdbVmapGetValue(histograms, arrayToString(h), 0 :: uint64);
            tdbVmapErase(histograms, arrayToString(h));
            for (uint64 j = 0; j < size(histogram); j++) {                      // for each cell of histogram h
                D bool eq = (pos == j);
                histogram[j] += (uint64)eq;
            }
            tdbVmapAddValue(histograms, arrayToString(h), histogram);
        }

    }
    return histograms;
}

/* Test Histogram */
// void main() {
//     uint64 cells = 3;
//     /* Test 1d histogram with floats */
//     pd_shared3p float64[[1]] data_float = {0.2,1.2,2.2,3.3,4.1,5,6.1,7,8.1};
//     pd_shared3p float64 min_float = min(data_float), max_float = max(data_float);
//     pd_shared3p uint64[[1]] hist_float = histogram(data_float, cells, min_float, max_float);
//     print(arrayToString(declassify(hist_float)));
//
//     /* Test 1d histogram with integers */
//     pd_shared3p uint64[[1]] data_int = {0,1,2,3,4,5,6,7,8};
//     pd_shared3p uint64 min_int = min(data_int), max_int = max(data_int);
//     pd_shared3p uint64[[1]] hist_int = histogram(data_int, cells, min_int, max_int);
//     print(arrayToString(declassify(hist_int)));
//
//     /* Test 2d histogram with floats */
//     pd_shared3p float64[[1]] data1 = {0,1,2,3,4,5,6,7,8}, data2 = {0,1,2,3,4,5,6,7,8};
//     pd_shared3p float64 min1_f = min(data1), max1_f = max(data1), min2_f = min(data2), max2_f = max(data2);
//     pd_shared3p uint64[[2]] hist = histogram(data1, data2, cells, cells, min1_f, max1_f, min2_f, max2_f);
//     print(arrayToString(declassify(hist)));
//
//     /* Test 2d histogram with integers */
//     pd_shared3p float64 min1_i = min(data1), max1_i = max(data1), min2_i = min(data2), max2_i = max(data2);
//     hist = histogram(data1, data2, cells, cells, min1_i, max1_i, min2_i, max2_i);
//     print(arrayToString(declassify(hist)));
//
//
//     pd_shared3p float64[[2]] data = reshape({1,2,3,4,1,3,5,2,2,4,3,2,7,6,4,1,6,3,2,2,6,2,5,3}, 6, 4);
//     pd_shared3p float64[[1]] mins = {1,2,2,1};
//     pd_shared3p float64[[1]] maxs = {7,6,5,4};
//     uint64[[1]] attributes = {0,1,3};
//     uint64[[1]] cells_list = {3,3,3};
//     uint64 histograms = multiple_1d_histograms(data, attributes, cells_list, mins, maxs);
//
//     pd_shared3p uint64[[1]] res = tdbVmapGetValue(histograms, "0", 0 :: uint64);
//     printVector(declassify(res));
//     res = tdbVmapGetValue(histograms, "1", 0 :: uint64);
//     printVector(declassify(res));
//     res = tdbVmapGetValue(histograms, "2", 0 :: uint64);
//     printVector(declassify(res));
//
//     pd_shared3p float64[[2]] data = reshape({1,2,3,4,
//                                             1,3,5,2,
//                                             2,4,3,2,
//                                             7,6,4,1,
//                                             6,3,2,2,
//                                             6,2,5,3}, 6, 4);
//     pd_shared3p float64[[1]] mins = {1,2,2,1};
//     pd_shared3p float64[[1]] maxs = {7,6,5,4};
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
//     uint64 histograms = multiple_histograms(data, 3::uint64, attributes_vmap, cells_vmap, mins, maxs);
//
//     pd_shared3p uint64[[1]] res = tdbVmapGetValue(histograms, "0", 0 :: uint64);
//     printVector(declassify(res));
//     res = tdbVmapGetValue(histograms, "1", 0 :: uint64);
//     printVector(declassify(res));
//     res = tdbVmapGetValue(histograms, "2", 0 :: uint64);
//     printVector(declassify(res));
// }

