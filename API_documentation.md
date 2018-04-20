##SMPC API
### SMPC Server
The SMPC Server interacts with the SMPC cluster. One can pose queries to the server and get answers resulting from the SMPC computation. For this purpose, the server provides the following RESTful API.

#### /smpc/histogram **[POST]**
>Initiate a secure histogram computation with desired parameters.

The basic functionality that the SMPC cluster provides is secure histogram computation. This is possible through the */smpc/histogram* POST request.

Through the request's body, one can specify all the desired properties of the histograms to be computed. These include the number of histograms, the attributes on which the histogram(s) will be built, the datasources from which data will be used, and a set of filters / conditions that should hold for each data tuple taken into consideration when building the histogram(s).

An example of the requests body can be found below.

```json
{
  "attributes": [
    [
      {
        "name": "Age",
        "cells": 5
      }
    ],
    [
      {
        "name": "Height",
        "cells": 3
      },
      {
        "name": "Weight",
        "cells": 4
      },
      {
        "name": "Heart Rate",
        "cells": 3
      }
    ]
  ],
  "datasources": [
    "HospitalA",
    "HospitalB"
  ],
  "filters": {
    "operator": "AND",
    "conditions": [
      {
        "attribute": "Sex",
        "operator": "=",
        "value": "Female"
      },
      {
        "attribute": "Age",
        "operator": ">",
        "value": "18"
      }
    ]
  }
}
```
The request is a JSON string consisting of the following parameters.
* `attributes`<span style="color:red">_required_</span> A list with an element (list) for each desired histogram. The length of this list is equal to the number of histograms that will be computed. For each histogram, one should provide a list of JSON objects, corresponding to the attributes on which this histogram will be built.
These JSON objects have the following keys:
    * `name`<span style="color:red">_required_</span> The name of the attribute (_string_).
    * `cells`<span style="color:red">_required_</span> The number of histogram cells/buckets to be created for this attribute (_positive integer_).
* `datasources`<span style="color:blue"> _optional_ </span> A list of the datasources (strings) from which the histogram(s) will be computed. If this key is left empty or not specified, all available datasources will be used.
* `filters`<span style="color:blue"> _optional_ </span> A JSON object containing a boolean operator and a list of filters / conditions that that should be met for each data tuple considered int the secure histogram computation. If this field is left blank or not specified, all data tuples will be used for the computation. The object has the following keys:
    * `operator`<span style="color:red">_required_</span> The boolean operator (_string_) that will be applied between all the specified conditions that follow. One of `[AND, OR, XOR]` In the case of multiple conditions, the operator is left-associative.
    * `conditions`<span style="color:red">_required_</span> The list of conditions that should be met by each data tuple in the computation. Each condition is represented as a JSON object with the following keys.
        * `attribute`<span style="color:red">_required_</span> The name of the attribute (_string_).
        * `operator`<span style="color:red">_required_</span> The condition's operator (_string_). One of `[>, <, =]`
        * `value`<span style="color:red">_required_</span> The attribute's value (_string_).

##### Server's response
The server's response to such a request is a list with an element for each of the computed histograms. Each such element contains a serialized version of each histograms, along with how many cells were used for each attribute / dimension of the histogram. An example response can be found below.
```json
[
  {
    "cellsPerDimension": [
      5
    ],
    "histogram": [
      237,
      211,
      239,
      161,
      152
    ]
  },
  {
    "cellsPerDimension": [
      3,
      4,
      3
    ],
    "histogram": [
      17,
      2,
      0,
      17,
      22,
      3,
      2,
      55,
      50,
      0,
      34,
      24,
      48,
      14,
      0,
      66,
      51,
      11,
      5,
      142,
      97,
      0,
      102,
      98,
      9,
      3,
      0,
      16,
      14,
      2,
      1,
      30,
      32,
      0,
      11,
      22
    ]
  }
]
```
The response is a list containing a JSON object for each computed histogram.
Each such object contains the following keys.
* `cellsPerDimension` A list with an element (_positive integer_) for each attribute of this histogram. These integers represent the amount of cells / buckets that were created for each attribute of this histogram.
* `histogram` A list of integers representing a serialized version of the computed histogram. Given the serialized histogram and the number of cells for each dimension / attribute, one can reconstruct the original multidimensional histogram.


___
### MHMD Driver
The MHMD Driver located on each hospital’s premises should support a RESTful API with current functionality the secure data importing into the SMPC cluster.  
#### /smpc/import **[POST]**
>Securely import data into the SMPC Platform.

The secure importing of a dataset into the SMPC cluster is initiated with the _/smpc/import_ POST request.

The request's body contains the path of the file with the desired dataset on the server responsible for this request. This should be a path to a .csv file compatible with the global data schema. An example request body can be found below.
```json
{
  "file": "/datasets/cvi_identified.csv"
}
```
The request body is a JSON string with the single following key:
* `file`<span style="color:red">_required_</span> The path of the file with the data to be securely imported.
