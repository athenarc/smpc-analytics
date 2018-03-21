import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

import shared3p_table_database;
import table_database;
import data_input;

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
    uint64 len = size(arr);
    for (uint64 i = 0; i < len; i++) {
        D uint64 cell = (uint64)((float64)(arr[i] - min) / cell_width);
        cell -= (uint64)(cell == cells);
        for (uint64 j = 0; j < cells; j++) {
            D uint64 eq = (uint64)(cell == j);
            output[j] += eq;
        }
    }
    return output;
}

/**
 * private arr: 1D array of all data. size M, where M: #attributes
 * public cells: number of the histogram's cell
 * private min: min value of arr
 * private max: max value of arr
**/
template <domain D, type T>
D uint64[[1]] histogram_simd(D T[[1]] arr, uint64 cells, D T min, D T max) {
    D uint64[[1]] output(cells);
    D float64 cell_width = ((float64) max - (float64) min) / (float64)cells;
    uint64 len = size(arr);
    D uint64[[1]] bitmap = (uint64)((float64)(arr-min)/cell_width);
    for (uint64 j = 0; j < cells; j++) {
        D uint64[[1]] eq = (uint64)(bitmap == j) + ((uint64)(bitmap == cells) * (uint64)(j == cells-1));
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
    // compute cell widths for each histogram
    uint64 cell_widths = tdbVmapNew();                                          // map of cell-widths for each histogram
    for (uint64 h = 0; h < number_of_histograms; h++) {                         // for each histogram
        uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
        uint64 length = product(cells);
        D uint64[[1]] histogram(length);
        tdbVmapAddValue(histograms, arrayToString(h), histogram);                  // initialize each histogram
        uint64 requested_attributes = size(cells);                                 // amount of attributes wanted for this histogram
        D float64[[1]] widths(requested_attributes);                                // widths for each cell of histogram h
        for (uint64 a = 0; a < requested_attributes; a++) {                        // for each attribute
            uint64 number_of_cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64)[a];
            D float64 max = maxs[tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a]];
            D float64 min = mins[tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a]];
            widths[a] = ((float64) max - (float64) min) / (float64)number_of_cells;
        }
        tdbVmapAddValue(cell_widths, arrayToString(h), widths);
    }

    uint64[[1]] array_shape = shape(arr);
    uint64 N = array_shape[0];                                                  // number of tuples
    for (uint64 t = 0; t < N; t++) {                                            // for each tuple
        for (uint64 h = 0; h < number_of_histograms; h++) {                     // for each histogram
            uint64[[1]] cells = tdbVmapGetValue(cells_vmap, arrayToString(h), 0 :: uint64);
            uint64 requested_attributes = size(cells);                             // amount of attributes wanted for this histogram

            D float64[[1]] widths = tdbVmapGetValue(cell_widths, arrayToString(h), 0 :: uint64);

            D uint64 pos = 0;                                                   // compute 1-d index from multiple indexes
            for (uint64 a = 0; a < requested_attributes; a++) {                    // for each attribute
                uint64 attribute = tdbVmapGetValue(attributes_vmap, arrayToString(h), 0 :: uint64)[a];
                D float64 value = arr[t, attribute];                            // value for column attributes[h] of tuple t

                D uint64 cell = (uint64)((float64)(value - (float64)mins[attribute]) / (float64)widths[a]);           // histogram cell that value belongs
                cell -= (uint64)(cell == cells[a]);
                uint64 prod = product(cells[a+1:]);
                pos += cell * prod;
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
void main() {
    /* Test 1d histogram with floats */
    uint64 cells = 3;
    pd_shared3p float64[[1]] data_float = {0,1,2,3,4,5,6,7,8,9};
    pd_shared3p float64 min_float = min(data_float), max_float = max(data_float);
    pd_shared3p uint64[[1]] hist_float = histogram(data_float, cells, min_float, max_float);
    print(arrayToString(declassify(hist_float)));


    /* Test 1d histogram with integers */
    pd_shared3p uint64[[1]] data_int = {0,1,2,3,4,5,6,7,8};
    pd_shared3p uint64 min_int = min(data_int), max_int = max(data_int);
    pd_shared3p uint64[[1]] hist_int = histogram(data_int, cells, min_int, max_int);
    print(arrayToString(declassify(hist_int)));


    /* Test multi-dimensional histogram with floats */
    pd_shared3p float64[[2]] data = reshape({0,1,2,3,4,5,6,7,8,9,
                                            0,1,2,3,4,5,6,7,8,9}, 2, 10);
    uint64[[1]] cells_list = {3,3};
    pd_shared3p float64[[1]] mins = {0,0};
    pd_shared3p float64[[1]] maxs = {9,9};
    printVector(declassify(histogram(data, cells_list, mins, maxs)));


    /* Test multiple_histograms with floats */
    pd_shared3p float64[[2]] data2 = reshape({1,2,3,4,
                                            1,3,5,2,
                                            2,4,3,2,
                                            7,6,4,1,
                                            6,3,2,2,
                                            6,2,5,3}, 6, 4);
    pd_shared3p float64[[1]] mins2 = {1,2,2,1};
    pd_shared3p float64[[1]] maxs2 = {7,6,5,4};

    uint64 attributes_vmap = tdbVmapNew();
    uint64[[1]] value = {1,2,3};
    tdbVmapAddValue(attributes_vmap, "0", value);
    value = {1,2};
    tdbVmapAddValue(attributes_vmap, "1", value);
    value = {2,3};
    tdbVmapAddValue(attributes_vmap, "2", value);

    uint64 cells_vmap = tdbVmapNew();
    value = {3,3,3};
    tdbVmapAddValue(cells_vmap, "0", value);
    value = {3,3};
    tdbVmapAddValue(cells_vmap, "1", value);
    value = {3,3};
    tdbVmapAddValue(cells_vmap, "2", value);

    uint64 histograms = multiple_histograms(data2, 3::uint64, attributes_vmap, cells_vmap, mins2, maxs2);

    pd_shared3p uint64[[1]] res = tdbVmapGetValue(histograms, "0", 0 :: uint64);
    printVector(declassify(res));
    res = tdbVmapGetValue(histograms, "1", 0 :: uint64);
    printVector(declassify(res));
    res = tdbVmapGetValue(histograms, "2", 0 :: uint64);
    printVector(declassify(res));


    /* Test multiple_histograms with imported data */
    uint64[[1]] array_shape = shape(array); // array -> variable from data_input.sc
    uint64 N = array_shape[0];
    uint64 M = array_shape[1];
    pd_shared3p float64[[1]] mins3(M);
    pd_shared3p float64[[1]] maxs3(M);
    for (uint64 j = 0; j < M; j++ ) {
      mins3[j] = min(array[:,j]);
      maxs3[j] = max(array[:,j]);
    }

    uint64 attributes_vmap2 = tdbVmapNew();
    uint64[[1]] value2 = {11,12};
    tdbVmapAddValue(attributes_vmap2, "0", value2);

    uint64 cells_vmap2 = tdbVmapNew();
    value2 = {3,5};
    tdbVmapAddValue(cells_vmap2, "0", value2);

    uint64 histograms2 = multiple_histograms(array, 1::uint64, attributes_vmap2, cells_vmap2, mins3, maxs3);
    res = tdbVmapGetValue(histograms2, "0", 0 :: uint64);
    printVector(declassify(res));
}
