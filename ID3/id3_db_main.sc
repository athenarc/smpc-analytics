import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

import oblivious;
import shared3p_oblivious;

import shared3p_table_database;
import table_database;
import data_input;
import id3_db;


void main() {
    left_br_str = bl_str("[ ");
    right_br_str = bl_str(" ]");
    eq_str = bl_str(" == ");
    space_str = bl_str(" ");
    arrow_str = bl_str(" --> ");
    left_curly_br_str = bl_str("{ ");
    right_curly_br_str = bl_str("}");

    // Create the data-providers list
    providers_vmap = tdbVmapNew();

    data_providers_num = 3;
    string table_0 = "id3_data_provider_0";
    string table_1 = "id3_data_provider_1";
    string table_2 = "id3_data_provider_2";
    tdbVmapAddString(providers_vmap, "0", table_0);
    tdbVmapAddString(providers_vmap, "0", table_1);
    tdbVmapAddString(providers_vmap, "0", table_2);

    print("Opening connection to db: ", datasource);
    tdbOpenConnection(datasource);

// for creating the db from original_examples (local use). Uncomment if necessary.
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

    // Open database before running operations on it
    // uint64 rows = tdbGetRowCount(datasource, table);

    pd_shared3p int64[[2]] original_example_indexes(data_providers_num, rows);
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        original_example_indexes[i,:] += 1; //simd
    }

    print("Running ID3 ...");
    pd_shared3p xor_uint8[[1]] root = id3(original_example_indexes, original_attributes[:columns-1]);
    print(bl_strDeclassify(root));
}
