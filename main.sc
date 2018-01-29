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
}
