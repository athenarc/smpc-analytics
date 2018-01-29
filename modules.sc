import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;

domain pd_shared3p shared3p;

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
