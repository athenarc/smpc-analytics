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
* weather = ['sun', 'wind', 'rain']
* relatives = ['yes', 'no']
* money = ['a-lot', 'little']
* day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
* month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]
* decision = ['cinema', 'kart', 'house', 'shopping']
**/

/**
 * typedef struct attribute {
 *	  uint64 count;
 *	  string data;
 * } Attribute;
**/

uint64 max_attribute_values = 12;
uint64 max_value_size = 10;
uint64 rows = 10;
uint64 columns = 6;



void main() {
    pd_shared3p xor_uint8[[3]] matrix(rows,columns,max_value_size);
    matrix[0,0,:] = bl_str("rain",max_value_size);
    matrix[0,1,:] = bl_str("yes",max_value_size);
    matrix[0,2,:] = bl_str("a-lot",max_value_size);
    matrix[0,3,:] = bl_str("Monday",max_value_size);
    matrix[0,4,:] = bl_str("August",max_value_size);
    matrix[0,5,:] = bl_str("shopping",max_value_size);

    matrix[1,0,:] = bl_str("wind",max_value_size);
    matrix[1,1,:] = bl_str("no",max_value_size);
    matrix[1,2,:] = bl_str("a-lot",max_value_size);
    matrix[1,3,:] = bl_str("Monday",max_value_size);
    matrix[1,4,:] = bl_str("September",max_value_size);
    matrix[1,5,:] = bl_str("cinema",max_value_size);

    matrix[2,0,:] = bl_str("sun",max_value_size);
    matrix[2,1,:] = bl_str("no",max_value_size);
    matrix[2,2,:] = bl_str("a-lot",max_value_size);
    matrix[2,3,:] = bl_str("Thursday",max_value_size);
    matrix[2,4,:] = bl_str("December",max_value_size);
    matrix[2,5,:] = bl_str("shopping",max_value_size);

    matrix[3,0,:] = bl_str("sun",max_value_size);
    matrix[3,1,:] = bl_str("no",max_value_size);
    matrix[3,2,:] = bl_str("a-lot",max_value_size);
    matrix[3,3,:] = bl_str("Friday",max_value_size);
    matrix[3,4,:] = bl_str("September",max_value_size);
    matrix[3,5,:] = bl_str("cinema",max_value_size);

    matrix[4,0,:] = bl_str("rain",max_value_size);
    matrix[4,1,:] = bl_str("no",max_value_size);
    matrix[4,2,:] = bl_str("a-lot",max_value_size);
    matrix[4,3,:] = bl_str("Tuesday",max_value_size);
    matrix[4,4,:] = bl_str("October",max_value_size);
    matrix[4,5,:] = bl_str("kart",max_value_size);

    matrix[5,0,:] = bl_str("wind",max_value_size);
    matrix[5,1,:] = bl_str("no",max_value_size);
    matrix[5,2,:] = bl_str("little",max_value_size);
    matrix[5,3,:] = bl_str("Thursday",max_value_size);
    matrix[5,4,:] = bl_str("September",max_value_size);
    matrix[5,5,:] = bl_str("shopping",max_value_size);

    matrix[6,0,:] = bl_str("wind",max_value_size);
    matrix[6,1,:] = bl_str("no",max_value_size);
    matrix[6,2,:] = bl_str("little",max_value_size);
    matrix[6,3,:] = bl_str("Monday",max_value_size);
    matrix[6,4,:] = bl_str("November",max_value_size);
    matrix[6,5,:] = bl_str("cinema",max_value_size);

    matrix[7,0,:] = bl_str("sun",max_value_size);
    matrix[7,1,:] = bl_str("no",max_value_size);
    matrix[7,2,:] = bl_str("little",max_value_size);
    matrix[7,3,:] = bl_str("Saturday",max_value_size);
    matrix[7,4,:] = bl_str("December",max_value_size);
    matrix[7,5,:] = bl_str("cinema",max_value_size);

    matrix[8,0,:] = bl_str("rain",max_value_size);
    matrix[8,1,:] = bl_str("no",max_value_size);
    matrix[8,2,:] = bl_str("little",max_value_size);
    matrix[8,3,:] = bl_str("Monday",max_value_size);
    matrix[8,4,:] = bl_str("April",max_value_size);
    matrix[8,5,:] = bl_str("shopping",max_value_size);

    matrix[9,0,:] = bl_str("sun",max_value_size);
    matrix[9,1,:] = bl_str("no",max_value_size);
    matrix[9,2,:] = bl_str("little",max_value_size);
    matrix[9,3,:] = bl_str("Sunday",max_value_size);
    matrix[9,4,:] = bl_str("December",max_value_size);
    matrix[9,5,:] = bl_str("kart",max_value_size);

    pd_shared3p xor_uint8[[3]] collection_attribute_values(columns,max_attribute_values,max_value_size);
    collection_attribute_values[0,0,:] = bl_str("sun",max_value_size);
    collection_attribute_values[0,1,:] = bl_str("wind",max_value_size);
    collection_attribute_values[0,2,:] = bl_str("rain",max_value_size);

    collection_attribute_values[1,0,:] = bl_str("yes",max_value_size);
    collection_attribute_values[1,1,:] = bl_str("no",max_value_size);

    collection_attribute_values[2,0,:] = bl_str("a-lot",max_value_size);
    collection_attribute_values[2,1,:] = bl_str("little",max_value_size);

    collection_attribute_values[3,0,:] = bl_str("Sunday",max_value_size);
    collection_attribute_values[3,1,:] = bl_str("Monday",max_value_size);
    collection_attribute_values[3,2,:] = bl_str("Tuesday",max_value_size);
    collection_attribute_values[3,3,:] = bl_str("Wednesday",max_value_size);
    collection_attribute_values[3,4,:] = bl_str("Thursday",max_value_size);
    collection_attribute_values[3,5,:] = bl_str("Friday",max_value_size);
    collection_attribute_values[3,6,:] = bl_str("Saturday",max_value_size);

    collection_attribute_values[4,0,:] = bl_str("January",max_value_size);
    collection_attribute_values[4,1,:] = bl_str("February",max_value_size);
    collection_attribute_values[4,2,:] = bl_str("March",max_value_size);
    collection_attribute_values[4,3,:] = bl_str("April",max_value_size);
    collection_attribute_values[4,4,:] = bl_str("May",max_value_size);
    collection_attribute_values[4,5,:] = bl_str("June",max_value_size);
    collection_attribute_values[4,6,:] = bl_str("July",max_value_size);
    collection_attribute_values[4,7,:] = bl_str("August",max_value_size);
    collection_attribute_values[4,8,:] = bl_str("September",max_value_size);
    collection_attribute_values[4,9,:] = bl_str("October",max_value_size);
    collection_attribute_values[4,10,:] = bl_str("November",max_value_size);
    collection_attribute_values[4,11,:] = bl_str("December",max_value_size);

    collection_attribute_values[5,0,:] = bl_str("cinema",max_value_size);
    collection_attribute_values[5,1,:] = bl_str("kart",max_value_size);
    collection_attribute_values[5,2,:] = bl_str("house",max_value_size);
    collection_attribute_values[5,3,:] = bl_str("shopping",max_value_size);

    pd_shared3p uint64[[2]] collection_attribute_counts(columns, max_attribute_values);

	/* for each value of the matrix */
    for (uint64 i = 0; i < columns; i++) {
        for (uint64 j = 0; j < rows; j++) {
            pd_shared3p xor_uint8[[1]] value = matrix[j,i,:];
            pd_shared3p xor_uint8[[2]] attribute_values = collection_attribute_values[i,:,:];

            for (uint64 k = 0 ; k < max_attribute_values ; k++) {
                pd_shared3p bool eq = bl_strEquals(attribute_values[k,:], value);
                collection_attribute_counts[i,k] += (uint64) eq;
            }
        }
        print(arrayToString(declassify(collection_attribute_counts[i,:])));
    }

}



