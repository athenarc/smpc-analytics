import shared3p;
import shared3p_random;
import shared3p_string;
import shared3p_sort;
import stdlib;

import oblivious;
import shared3p_oblivious;

import shared3p_table_database;
import table_database;

domain pd_shared3p shared3p;

string datasource = "DS1";

template <domain D, type T>
D bool exists(D T[[1]] arr, uint64 len, D T element) {
    D uint64 exists = 0;
    for (uint64 i = 0; i < len; i++) {
        exists += (uint64)(arr[i] == element);
    }
    return exists > 0;
}

// Create the data-providers list
uint64 createDataProviders(uint64 data_providers_num, uint64 rows, uint64 columns, pd_shared3p float64[[2]] original_examples, bool print_messages) {
    uint64 providers_vmap = tdbVmapNew();
    string table_0 = "data_provider_0";
    string table_1 = "data_provider_1";
    string table_2 = "data_provider_2";
    tdbVmapAddString(providers_vmap, "0", table_0);
    tdbVmapAddString(providers_vmap, "0", table_1);
    tdbVmapAddString(providers_vmap, "0", table_2);

    // Open database before running operations on it
    if (print_messages) {
        print("Opening connection to db: ", datasource);
    }
    tdbOpenConnection(datasource);
    // for creating the db from original_examples (local use). Uncomment if necessary.
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        if (print_messages) {
            print("Table: " + table);
        }
        // Check if a table exists
        if (tdbTableExists(datasource, table)) {
          // Delete existing table
          if (print_messages) {
              print("Deleting existing table: ", table);
          }
          tdbTableDelete(datasource, table);
        }
        if (print_messages) {
            print("Creating new table: ", table);
        }
        pd_shared3p float64 vtype;
        tdbTableCreate(datasource, table, vtype, columns);

        if (print_messages) {
            print("Inserting data to table " + table + "...");
        }
        pd_shared3p float64[[1]] row;
        for (uint j = 0; j < rows; ++j) {
            row = original_examples[j,:];
            row += (float64)(i);            // Dummy operation to have different values
            tdbInsertRow(datasource, table, row);
            if (print_messages) {
                printVector(declassify(row));
            }
        }
        if (print_messages) {
            print("Done inserting in table " + table + "\n\n");
        }
    }
    for (uint64 d = 0 ; d < data_providers_num ; d++) {
        string table = tdbVmapGetString(providers_vmap, "0", d :: uint64);
        if (print_messages) {
            print("Printing from table " + table + "");
        }
        for (uint j = 0; j < columns; ++j) {
            pd_shared3p float64[[1]] res = tdbReadColumn(datasource, table, j :: uint64);
            if (print_messages) {
                printVector(declassify(res));
            }
        }
    }
    return providers_vmap;
}

void main() {
    uint64 rows = 8;
    uint64 columns = 3;
    pd_shared3p float64[[2]] data = reshape({1,5,8,
                                            3,6,9,
                                            3,6,11,
                                            1,6,10,
                                            2,7,9,
                                            3,5,8,
                                            4,5,11,
                                            2,6,10}, rows, columns);

    // Initialize 3 data-providers' data, each table has 8 rows and 3 columns of identical data.
    uint64 data_providers_num = 3;
    uint64 providers_vmap = createDataProviders(data_providers_num, rows, columns, data, true);

    // Compute unique values
    uint64 possible_values_vmap = tdbVmapNew();

    for (uint64 d = 0 ; d < data_providers_num ; d++) {
        string table = tdbVmapGetString(providers_vmap, "0", d :: uint64);

        for (uint64 j = 0 ; j < columns ; j++) {
            pd_shared3p float64[[1]] data_from_provider = tdbReadColumn(datasource, table, j :: uint64); // read column j

            pd_shared3p float64[[1]] uniques(rows); // initialize uniques with rows size
            uint64 unique_cnt = 0;
            for (uint64 i = 0 ; i < rows ; i++) {

                bool exists = declassify(exists(uniques, unique_cnt, data_from_provider[i]));
                /**
                 * Leakage Evaluation:
                 *  Someone can infer the number and the positions of unique values.
                 *  However, the values themselves are encrypted.
                **/
                if (!exists) {
                    uniques[unique_cnt] = data_from_provider[i];
                    unique_cnt++;
                }
            }
            uniques = uniques[0:unique_cnt]; // keep only the uniques
            tdbVmapAddValue(possible_values_vmap, arrayToString(j), uniques);
        }
    }

    print("\n\nPrinting possible-values: ");
    for (uint64 d = 0 ; d < data_providers_num ; d++) {
        print("Data Provider ", d, ":");

        for (uint64 j = 0 ; j < columns ; j++) {
            pd_shared3p float64[[1]] res = tdbVmapGetValue(possible_values_vmap, arrayToString(j), d :: uint64);
            printVector(declassify(res));
            print("\n");
        }
    }

}

