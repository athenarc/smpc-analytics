import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

import oblivious;
import shared3p_oblivious;

import shared3p_table_database;
import table_database;
import id3_db_categorical;

/**
 * Gender (0) : int64,
 * Height (cm) (1) : int64,
 * Weight (kg) (2) : int64,
 * Patient Age (3) : int64,
**/


void main() {
    columns = 4;
    max_attribute_values = 4;
    class_index = 3;
    original_attributes = {0,1,2,3};
    possible_values = reshape({0,1,-1,-1,
        0,1,2,3,
        0,1,2,3,
        0,1,2,3}, columns, max_attribute_values);
    pd_shared3p uint64[[1]] original_attributes_without_class = {0,1,2};

    quote = bl_str("\"");
    comma = bl_str(", ");
    eq_str = bl_str(" == ");
    space = bl_str(" ");
    colon = bl_str(": ");
    left_curly_br = bl_str("{ ");
    right_curly_br = bl_str("}");

    // Create the data-providers list
    providers_vmap = tdbVmapNew();

    data_providers_num = 1;
    string table_0 = "data_1000";
    // string table_1 = "id3_data_provider_1_num";
    // string table_2 = "id3_data_provider_2_num";
    tdbVmapAddString(providers_vmap, "0", table_0);
    // tdbVmapAddString(providers_vmap, "0", table_1);
    // tdbVmapAddString(providers_vmap, "0", table_2);

    // Open database before running operations on it
    print("Opening connection to db: ", datasource);
    tdbOpenConnection(datasource);

// for creating the db from original_examples (local use). Uncomment if necessary.
    // pd_shared3p int64[[2]] original_examples(rows, columns) = reshape({0,0,1,3,0,0,0,1,1,3,2,1,1,3,2,1,0,1,1,2,0,0,0,0,1,2,3,0,1,2,1,2,0,0,1,3,1,2,3,3,1,2,3,1,1,2,2,2,1,2,3,0,0,0,0,3,1,3,3,1,1,2,3,1,0,1,1,1,0,1,1,2,1,2,3,1,1,2,2,3,1,2,3,3,1,2,2,3,1,3,3,0,1,3,3,3,1,2,2,3,1,3,1,0,1,3,3,2,1,2,3,0,0,1,0,3,1,2,2,1,1,2,3,1,1,2,1,2,0,1,0,2,1,2,3,0,1,3,2,0,1,2,3,1,0,0,0,2,1,2,3,3,1,2,3,1,1,3,2,1,1,3,2,2,0,1,1,0,1,2,2,1,1,3,3,3,1,2,3,1,1,2,2,0,1,2,1,3,1,3,2,0,1,3,3,0,1,3,3,0,1,2,1,2,1,2,1,1,0,1,1,2,1,2,3,0,0,0,0,2,0,0,1,1,1,3,2,3,1,3,3,2,1,2,2,0,0,0,1,3,1,3,3,3,1,3,3,3,0,0,0,1,0,1,0,2,0,1,1,0,1,2,1,0,1,3,3,2,1,1,2,3,1,3,3,1,0,0,1,0,1,1,3,0,1,2,3,0,1,1,3,3,0,1,1,0,1,3,2,0,1,2,1,3,1,2,3,2,1,3,2,3,0,1,0,1,0,0,0,3,1,2,2,0,0,2,1,2,0,1,2,0,0,1,1,1,1,1,2,1,0,1,1,0,1,3,2,3,1,3,3,1,0,0,0,3,0,0,0,1,1,3,2,2,1,2,2,1,1,2,1,0,1,2,2,3,1,1,2,1,1,3,2,1,1,2,2,0,1,2,2,1,1,2,2,3,1,3,2,3}, 100, 4);
    //
    // for (uint64 i = 0 ; i < data_providers_num ; i++) {
    //     string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
    //     print("Table: " + table);
    //
    //     // Check if a table exists
    //     if (tdbTableExists(datasource, table)) {
    //       // Delete existing table
    //       print("Deleting existing table: ", table);
    //       tdbTableDelete(datasource, table);
    //     }
    //
    //     print("Creating new table: ", table);
    //     pd_shared3p int64 vtype;
    //     tdbTableCreate(datasource, table, vtype, columns);
    //
    //     print("Inserting data to table " + table + "...");
    //     pd_shared3p int64[[1]] row;
    //     for (uint i = 0; i < rows; ++i) {
    //         row = original_examples[i,:];
    //         tdbInsertRow(datasource, table, row);
    //     }
    //     print("Done inserting in table " + table + "\n\n");
    // }

    uint64 original_example_indexes_vmap = tdbVmapNew();
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        uint64 rows = tdbGetRowCount(datasource, table);
        pd_shared3p int64[[1]] original_example_indexes(rows);
        original_example_indexes = 1;
        tdbVmapAddValue(original_example_indexes_vmap, "0", original_example_indexes);
    }

    print("Running ID3 ...");
    pd_shared3p xor_uint8[[1]] root = id3(original_example_indexes_vmap, original_attributes_without_class);
    print(bl_strDeclassify(root));
}
