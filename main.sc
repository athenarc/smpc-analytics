import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;


void main() {
    uint64 len1 = 9;
    pd_shared3p float64[[1]] data1_f = {-0.6, 0.0, 1.0, -2.0, 3.0, 4.6, -5.0, 6.0, 7.0, 8.0};
    pd_shared3p float64 min = min(data1_f);
    print(declassify(min));

    pd_shared3p uint64[[1]] data1_i = { 4, 5, 8, 7, 1, 2, 10, 3, 6, 9};
    pd_shared3p float64 median = median((uint64)data1_i);
    print(declassify(median));

    pd_shared3p uint64 idx = exists_in_index(data1_f, min);
    print(declassify(idx));

    pd_shared3p uint64 num = 8;
    idx = exists_in_index(data1_i, num);
    print(declassify(idx));

    pd_shared3p bool ex = exists(data1_i, num);
    print(declassify(ex));

}
