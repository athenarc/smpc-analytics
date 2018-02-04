import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

domain pd_shared3p shared3p;

/**
 * ID3 Summary
 * 1. Calculate the entropy of every attribute using the data set
 * 2. Split the set into subsets using the attribute for which the resulting entropy
 * 	  (after splitting) is minimum (or, equivalently, information gain is maximum)
 * 3. Make a decision tree node containing that attribute
 * 4. Recurse on subsets using remaining attributes.
**/

uint64 rows = 14;
uint64 columns = 5;
uint64 possible_classes = 2;
pd_shared3p int64[[2]] original_examples(rows,columns) = reshape({0,0,1,0,1,
                                                                    0,0,1,1,1,
                                                                    1,0,1,0,0,
                                                                    2,1,1,0,0,
                                                                    2,2,0,0,0,
                                                                    2,2,0,1,1,
                                                                    1,2,0,1,0,
                                                                    0,1,1,0,1,
                                                                    0,2,0,0,0,
                                                                    2,1,0,0,0,
                                                                    0,1,0,1,0,
                                                                    1,1,1,1,0,
                                                                    1,0,0,0,0,
                                                                    2,1,1,1,1}, rows, columns);


pd_shared3p uint64 mylen(pd_shared3p int64[[2]] array){
    pd_shared3p uint64 len = 0;
    uint64[[1]] dims = shape(array);
    for(uint64 i = 0; i < dims[0]; i++){
        len += (uint64)(array[i,0] != -1);
    }
    return len;
}

pd_shared3p bool all_examples_same(pd_shared3p int64[[2]] examples){
    uint64[[1]] dims = shape(examples);
    uint64 rows = dims[0];
    uint64 columns = dims[1];
    pd_shared3p uint64 res = 0;
    pd_shared3p uint64[[1]] class_counts(possible_classes);
    for(uint64 c = 0; c < possible_classes; c++){
        for(uint64 i = 0; i < rows; i++){
            pd_shared3p bool neq = (examples[i,columns-1] == (int64)c);
            class_counts[c] += (uint64)(neq); // counter for class i
        }
        res += (uint64)(class_counts[c] == mylen(examples));
    }
    return (bool)res;
}

void main() {
    print(arrayToString(declassify(original_examples)));
    print(declassify(all_examples_same(original_examples)));
}



