import shared3p;
import shared3p_random;
import shared3p_sort;
import stdlib;
import modules;

import shared3p_table_database;
import table_database;

/**
 * private arr: 1D array of all data. size M, where M: #attributes
 * public cells: number of the histogram's cell
 * private min: min value of arr
 * private max: max value of arr
**/
template <domain D, type T>
D uint64[[1]] histogram(D T[[1]] arr, uint64 cells, D T min, D T max) {
    D uint64[[1]] output(cells);
    D float64 cell_width = ((float64) max - (float64) min) / (float64)cells;
    D uint64[[1]] bitmap = (uint64)((float64)(arr-min)/cell_width);
    for (uint64 j = 0; j < cells; j++) {
        D uint64[[1]] eq = (uint64)(bitmap == j) + ((uint64)(bitmap == cells) * (uint64)(j == cells-1));
        output[j] = sum(eq);
    }
    return output;
}

/**
 * public string datasource: name of the datasource
 * public uint64 providers_vmap: A tdb-Vmap with key 0 and value an array of the data-provider names
 * public uint64 data_providers_num: the number of data-providers
 * public uint64 index: column index in the table
 * public cells: number of the histogram's cell
 * private min: min value of arr
 * private max: max value of arr
**/
template <domain D, type T>
D uint64[[1]] histogram(string datasource, uint64 providers_vmap, uint64 data_providers_num, uint64 index, uint64 cells, D T min, D T max) {
    D uint64[[1]] result(cells);
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        string table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        print("Computing aggregates for data-provider " + table);
        D T[[1]] column = tdbReadColumn(datasource, table, index);
        result += histogram(column, cells, min, max);
    }
    return result;
}


/* public data */
string datasource = "DS1";
uint64 data_providers_num = 3;
uint64 columns = 5;
uint64 rows = 14;
string table_1 = "data_provider_1";
string table_2 = "data_provider_2";
string table_3 = "data_provider_3";


pd_shared3p uint64[[2]] random_data(rows, columns) = reshape({0,2,1,0,1,
                                                              0,0,1,2,1,
                                                              1,0,1,0,2,
                                                              2,1,1,0,0,
                                                              2,2,0,0,0,
                                                              2,2,0,1,1,
                                                              1,2,0,1,0,
                                                              0,1,1,2,1,
                                                              0,2,0,2,0,
                                                              2,1,0,2,0,
                                                              0,1,2,1,0,
                                                              1,1,2,1,0,
                                                              1,2,0,0,0,
                                                              2,1,1,1,1}, rows, columns);


void main() {
    // Create the data-providers list
    uint64 providers_vmap = tdbVmapNew();
    tdbVmapAddString(providers_vmap, "0", table_1);
    tdbVmapAddString(providers_vmap, "0", table_2);
    tdbVmapAddString(providers_vmap, "0", table_3);

    string table;
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        print(table);
    }


    // Open connection to DB and Insert data to different tables
    print("Opening connection to db: ", datasource);
    tdbOpenConnection(datasource);
    for (uint64 i = 0 ; i < data_providers_num ; i++) {
        table = tdbVmapGetString(providers_vmap, "0", i :: uint64);
        print("Table: " + table);

        pd_shared3p uint64 data_type;
        // Check if a table exists
        if (tdbTableExists(datasource, table)) {
          // Delete existing table
          print("Deleting existing table: ", table);
          tdbTableDelete(datasource, table);
        }

        print("Creating new table: ", table);
        tdbTableCreate(datasource, table, data_type, columns);
        print("Inserting data to table " + table + "...");
        for (uint64 i = 0 ; i < rows ; i++) {
          tdbInsertRow(datasource, table, random_data[i,:]);
        }
        print("Done inserting in table " + table + "\n\n");
    }
    print("Done inserting!");

    uint64 cells = 3;
    uint64 index = 0;
    pd_shared3p uint64 min_int = 0, max_int = 2;

    pd_shared3p uint64[[1]] hist = histogram(datasource, providers_vmap, data_providers_num, index, cells, min_int, max_int);
    print(arrayToString(declassify(hist)));

}
