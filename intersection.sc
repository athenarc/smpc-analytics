import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

template <domain D, type T>
D T[[1]] intersection(D T[[1]] set1, D T[[1]] set2) {
    uint64 len1 = size(set1);
    uint64 len2 = size(set2);
    uint64 min_len = min(len1, len2);
    uint64 max_len = len1 + len2 - min_len;
    D T[[1]] min_set = len1 < len2 ? set1 : set2;
    D T[[1]] max_set = len1 > len2 ? set1 : set2;

    D T[[1]] intersection(min_len);

    for (uint64 i = 0 ; i < min_len ; i++) {
        for (uint64 j = 0 ; j < max_len ; j++) {
            D T eq = (T) (min_set[i] == max_set[j]);
            intersection[i] += (eq * min_set[i]);
        }
    }
    return shuffle(intersection);
}

/* Test Intersection */
// void main() {
//     /* Test with integers */
//    pd_shared3p uint64[[1]] set1_int = {9, 10, 1, 12, 14, 13, 5, 6, 8, 17};
//    pd_shared3p uint64[[1]] set2_int = {10, 11, 12, 3, 14, 5, 6, 17, 8};
//    pd_shared3p uint64[[1]] intersection_int = intersection(set1_int, set2_int);
//    print(arrayToString(declassify(intersection_int)));
//
//    /* Test with floats */
//    pd_shared3p float64[[1]] set1_float = {9.0, 10.0, 1.0, 12.1, 14.1, 13.0, 5.2, 6.2, 8.6, 17.1};
//    pd_shared3p float64[[1]] set2_float = {10.0, 11.0, 12.0, 3.1, 14.1, 5.0, 6.2, 17.2, 8.6};
//    pd_shared3p float64[[1]] intersection_float = intersection(set1_float, set2_float);
//    print(arrayToString(declassify(intersection_float)));
// }
