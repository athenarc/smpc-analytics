
import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

import oblivious;
import shared3p_oblivious;

import shared3p_table_database;
import table_database;
import c45_db;

void main(){
    string table_0 = "c45_test";
    // Create the data-providers list
    providers_vmap = tdbVmapNew();
    data_providers_num = 1;

    tdbVmapAddString(providers_vmap, "0", table_0);


    original_attributes = {0,1,2,3,4};
    uint64[[1]] original_attributes_without_class = {0,1,2,3};
    class_index = 4;

    columns = 5;

    datasource = "DS1";
    categorical_attributes = {-1};

    class_min = 0;
    class_max = 100;
    class_cells = 3;

    print("Opening connection to db: ", datasource);
    tdbOpenConnection(datasource);


    possible_values = tdbVmapNew();
    float64[[1]] values;
    values = {0,1,2};
    tdbVmapAddValue(possible_values, "4", values);


    uint64 original_example_indexes_vmap = tdbVmapNew();
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        uint64 rows = tdbGetRowCount(datasource, table);
        pd_shared3p int64[[1]] original_example_indexes(rows);
        original_example_indexes = 1;
        tdbVmapAddValue(original_example_indexes_vmap, "0", original_example_indexes);
    }

    print("Running C4.5 ...");
    string root = c45(original_example_indexes_vmap, original_attributes_without_class);
    print(root);

    // for (uint64 i = 0 ; i < data_providers_num ; i++) {
    //     string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
    //     // Check if a table exists
    //     if (tdbTableExists(datasource, table)) {
    //       // Delete existing table
    //       print("Deleting table: ", table);
    //       tdbTableDelete(datasource, table);
    //     }
    // }
}