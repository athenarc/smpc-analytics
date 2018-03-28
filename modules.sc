import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;

domain pd_shared3p shared3p;

float64 FLOAT64_POS_MIN = 0.00000000000001;

pd_shared3p float64 min(pd_shared3p float64 x, pd_shared3p float64 y){
    return (x+y)/2 - abs(x-y)/2;
}

pd_shared3p float64 max(pd_shared3p float64 x, pd_shared3p float64 y){
    return (x+y)/2 + abs(x-y)/2;
}

pd_shared3p float64 min(pd_shared3p float64[[1]] arr){
    pd_shared3p float64 min = arr[0];
    uint64 len = size(arr);
    for(uint i = 1; i < len; ++i){
        min = min(min, arr[i]);
    }
    return min;
}

pd_shared3p float64 max(pd_shared3p float64[[1]] arr){
    pd_shared3p float64 max = arr[0];
    uint64 len = size(arr);
    for(uint i = 1; i < len; ++i){
        max = max(max, arr[i]);
    }
    return max;
}

pd_shared3p float64 median(pd_shared3p uint64[[1]] arr){
    pd_shared3p uint64[[1]] sorted = quicksort(arr);
    uint64 len = size(arr);
    if(len % 2 == 1){
        return (float64)sorted[len/2];
    }
    return ((float64)sorted[(len/2)-1] + (float64)sorted[len/2]) / 2;
}

template <domain D, type T>
D bool exists(D T[[1]] arr, D T element) {
    D uint64 exists = 0;
    for (uint64 i = 1; i < size(arr); i++) {
        exists += (uint64)(arr[i] == element);
    }
    return exists > 0;
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

