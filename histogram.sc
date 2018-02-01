import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

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
// }
