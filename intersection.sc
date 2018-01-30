import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

pd_shared3p float64[[1]] intersection(pd_shared3p float64[[1]] set1, pd_shared3p float64[[1]] set2) {
    uint64 len1 = size(set1);
    uint64 len2 = size(set2);
    uint64 min_len = min(len1, len2);
    uint64 max_len = len1 + len2 - min_len;
    pd_shared3p float64[[1]] min_set = len1 < len2 ? set1 : set2;
    pd_shared3p float64[[1]] max_set = len1 > len2 ? set1 : set2;

    pd_shared3p float64[[1]] intersection(min_len);

    for (uint64 i = 0 ; i < min_len ; i++) {
        for (uint64 j = 0 ; j < max_len ; j++) {
            pd_shared3p float64 eq = (float64) (min_set[i] == max_set[j]);
            intersection[i] += (eq * min_set[i]);
        }
    }
    return shuffle(intersection);
}

pd_shared3p uint64[[1]] intersection(pd_shared3p uint64[[1]] set1, pd_shared3p uint64[[1]] set2) {
    uint64 len1 = size(set1);
    uint64 len2 = size(set2);
    uint64 min_len = min(len1, len2);
    uint64 max_len = len1 + len2 - min_len;
    pd_shared3p uint64[[1]] min_set = len1 < len2 ? set1 : set2;
    pd_shared3p uint64[[1]] max_set = len1 > len2 ? set1 : set2;

    pd_shared3p uint64[[1]] intersection(min_len);

    for (uint64 i = 0 ; i < min_len ; i++) {
        for (uint64 j = 0 ; j < max_len ; j++) {
            pd_shared3p uint64 eq = (uint64) (min_set[i] == max_set[j]);
            intersection[i] += (eq * min_set[i]);
        }
    }
    return shuffle(intersection);
}

/* Test Intersection */
//void main() {
//    pd_shared3p uint64[[1]] set1 = {9, 10, 1, 12, 14, 13, 5, 6, 8, 17};
//    pd_shared3p uint64[[1]] set2 = {10, 11, 12, 3, 14, 5, 6, 17, 8};
//    pd_shared3p uint64[[1]] intersection = intersection(set1, set2);
//    print(_vectorToString(declassify(intersection)));
//}
