import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

pd_shared3p uint64[[1]] histogram(pd_shared3p uint64[[1]] arr, uint64 cells, pd_shared3p uint64 min, pd_shared3p uint64 max){
    pd_shared3p uint64[[1]] output(cells);
    pd_shared3p uint64 cell_width = (uint64)ceiling((float64)(max+1 - min) / (float64)cells);
    uint64 len = size(arr);
    for(uint64 i = 0; i < len; i++){
        pd_shared3p uint64 cell = arr[i] / cell_width;
        for(uint64 j = 0; j < cells; j++){
            pd_shared3p bool eq = (cell == j);
            output[j] += (uint64)eq;
        }
    }
    return output;
}

pd_shared3p uint64[[1]] histogram(pd_shared3p float64[[1]] arr, uint64 cells, pd_shared3p float64 min, pd_shared3p float64 max){
    pd_shared3p uint64[[1]] output(cells);
    pd_shared3p uint64 cell_width = (uint64)ceiling((max+1 - min) / (float64)cells);
    uint64 len = size(arr);
    for(uint64 i = 0; i < len; i++){
        pd_shared3p uint64 cell = (uint64)(arr[i] / (float64)cell_width);
        for(uint64 j = 0; j < cells; j++){
            pd_shared3p bool eq = (cell == j);
            output[j] += (uint64)eq;
        }
    }
    return output;
}

pd_shared3p uint64[[2]] histogram(pd_shared3p float64[[1]] arr1, pd_shared3p float64[[1]] arr2, uint64 cells1, uint64 cells2, pd_shared3p float64 min1, pd_shared3p float64 max1, pd_shared3p float64 min2, pd_shared3p float64 max2){
    pd_shared3p uint64[[2]] output(cells1, cells2);
    pd_shared3p uint64 cell_width1 = (uint64)ceiling((max1+1 - min1) / (float64)cells1);
    pd_shared3p uint64 cell_width2 = (uint64)ceiling((max2+1 - min2) / (float64)cells2);
    uint64 len = size(arr1);
    for(uint64 k = 0; k < len; k++){
        pd_shared3p uint64 cell1 = (uint64)(arr1[k] / (float64)cell_width1);
        pd_shared3p uint64 cell2 = (uint64)(arr2[k] / (float64)cell_width2);
        for(uint64 i = 0; i < cells1; i++){
            for(uint64 j = 0; j < cells2; j++){
                pd_shared3p bool eq1 = (cell1 == i);
                pd_shared3p bool eq2 = (cell2 == j);
                output[i,j] += (uint64)(eq1) * (uint64)(eq2);
            }
        }
    }
    return output;
}

/* Test Histogram */
// void main() {
//     pd_shared3p float64[[1]] data1_f = {0,1,2,3,4,5,6,7,8};
//     pd_shared3p float64[[1]] data2_f = {0,1,2,3,4,5,6,7,8};
//     pd_shared3p float64 min1 = min(data1_f);
//     pd_shared3p float64 max1 = max(data1_f);
//     pd_shared3p float64 min2 = min(data2_f);
//     pd_shared3p float64 max2 = max(data2_f);
//     uint64 cells = 3;
//     pd_shared3p uint64[[2]] hist = histogram(data1_f, data2_f, cells, cells, min1, max1, min2, max2);
//     for(uint64 i = 0; i < cells; i++){
//         for(uint64 j = 0; j < cells; j++){
//             print(declassify(hist[i,j]));
//         }
//         print("\n");
//     }
// }
