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

/**
 * weather = ['sun', 'wind', 'rain'] 																// = [0, 1, 2]
 * relatives = ['yes', 'no'] 																		// = [0, 1]
 * money = ['a-lot', 'little'] 																		// = [0, 1]
 * day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] 			// = [0, 1, 2, 3, 4, 5, 6]
 * month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]	// = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
 * decision = ['cinema', 'kart', 'house', 'shopping'] 												// = [0, 1, 2, 3]
**/

/**
 * typedef struct attribute {
 *	  uint64 count;
 *	  string data;
 * } Attribute;
**/


uint64 max_attribute_values = 12;
uint64 rows = 10;
uint64 columns = 6;
pd_shared3p uint64[[1]] attribute_sizes(columns) = { 3, 2, 2, 7, 12, 4 };

void main() {
    /* Generate Input */
    pd_shared3p uint64[[2]] matrix(rows, columns);

    for (uint64 i = 0; i < rows; i++) {
        matrix[i,:] = randomize(matrix[i,:]) % attribute_sizes;
        print(arrayToString(declassify(matrix[i,:])));
    }
	print("\n");

    pd_shared3p int64[[2]] collection_attribute_values(columns, max_attribute_values);
    for (uint64 i = 0; i < columns; i++) {
        for (uint64 j = 0; j < max_attribute_values ; j++) {
            pd_shared3p bool eq = j < attribute_sizes[i];
            collection_attribute_values[i,j] = (int64)eq * (int64)j + ((1 - (int64)eq) * (-1));
        }
    }
    print(arrayToString(declassify(collection_attribute_values)));
	print("\n");

	/* Compute Counts (count-vector) for each attribute */
    pd_shared3p uint64[[2]] collection_attribute_counts(columns, max_attribute_values);
    for (uint64 i = 0; i < columns; i++) {
        for (uint64 j = 0; j < rows; j++) {
            pd_shared3p int64 value = (int64)matrix[j,i];
            pd_shared3p int64[[1]] attribute_values = collection_attribute_values[i,:];

            for (uint64 k = 0 ; k < max_attribute_values ; k++) {
                pd_shared3p bool eq = (attribute_values[k] == value);
                collection_attribute_counts[i,k] += (uint64) eq;
            }
        }
        print(arrayToString(declassify(collection_attribute_counts[i,:])));
    }
    print("\n");

}



