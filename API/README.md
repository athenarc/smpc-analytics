## SMPC API
### SMPC Server
The SMPC Server interacts with the SMPC cluster. One can pose queries to the server and get answers resulting from the SMPC computation. For this purpose, the server provides the following RESTful API.

#### /smpc/count **[POST]**
>Initiate a secure count computation on a specified attribute.

You can get the securely computed counts for some specified Mesh terms.

Through the request's body, one can specify the desired Mesh terms. The values the count of which will be computed are the children of the specified Mesh term from the Mesh ontology. For example, if a user specifies that she wants the counts for the Mesh term _Age Groups_ `[M01.060]` , she will get 4 counts back corresponding to the four children of _Age Groups_, namely _Adolescent_ `[M01.060.057]`, _Adult_`[M01.060.116]`, _Child_`[M01.060.406]` and _Infant_`[M01.060.703]`.
If the specified Mesh terms are two, then the resulting counts will correspond to tuples of Mesh labels. If the specified Mesh terms are three, the result will be triples, etc.

An example of the requests body can be found below.

```json
{
    "attributes": [
        "M01.060"
    ],
    "datasources": [
      "HospitalA",
      "HospitalB"
    ]
}
```
The request is a JSON string consisting of the following parameters.
* `attributes` <span style="color:red">_required_</span> A list of the ids of the Mesh terms for which the counts should be computed.
* `datasources` <span style="color:blue">_optional_</span> A list of the datasources (strings) from which the counts will be computed. If this key is left empty or not specified, all available datasources will be used.

##### Server's response
The secure count computation is a potentially long running operation. For that reason the server's response to such a request is always `HTTP/1.1 202 Accepted`, along with a location in which one should periodically poll for the computation's status and/or result. An example response can be found below.
```json
{
  "location": "/smpc/queue?request=d491977f-88e7-4993-aaeb-c8244b320faf"
}
```
In order to check for the secure count computation's status, and/or retrieve the result you should periodically poll the above location using the `/smpc/queue` GET request, which is described below.


#### /smpc/decision-tree **[POST]**
>Train a decision tree classifier on specific test and target attributes.

You can request a decision tree building based on specified training attributes and also a specified class / target attribute.

An example of the requests body can be found below.

```json
{
  "attributes": [
    {
      "name": "Height (cm)",
      "cells": "3"
    },
    {
      "name": "Weight (kg)",
      "cells": "3"
    }
  ],
  "classifier": "ID3",
  "class_attribute": {
    "name": "Patient Age",
    "cells": "3"
  },
  "dataset": "cvi",
  "datasources": [
    "HospitalA",
    "HospitalB"
  ]
}
```
The request is a JSON object consisting of the following parameters.
* `attributes` <span style="color:red">_required_</span> A list of the training attributes. Each attribute is a JSON object of the following form:
    * `name` <span style="color:red">_required_</span> The name of the attribute
    * `cells` <span style="color:blue">_optional_</span> The desired cells / ranges. This is required only if the attribute is continuous and the classification algorithm is ID3.
* `class_attribute` <span style="color:red">_required_</span> The class / target attribute. The class attribute is a JSON object of the following form:
    * `name` <span style="color:red">_required_</span> The name of the attribute
    * `cells` <span style="color:blue">_optional_</span> The desired cells / ranges. This is required only if the class attribute is continuous.
* `dataset` <span style="color:red">_required_</span> The dataset to be used for the classification training.
* `classifier` <span style="color:red">_required_</span> The classification algorithm. One of `[ID3, C45]`.
* `datasources` <span style="color:blue">_optional_</span> A list of the datasources (strings) from which the counts will be computed. If this key is left empty or not specified, all available datasources will be used.


##### Server's response
The secure decision tree creation is a long running operation. For that reason the server's response to such a request is always `HTTP/1.1 202 Accepted`, along with a location in which one should periodically poll for the computation's status and/or result. An example response can be found below.
```json
{
  "location": "/smpc/queue?request=bc801fcc-1521-4143-92e4-bbd93f9bb131"
}
```
In order to check for the secure count computation's status, and/or retrieve the result you should periodically poll the above location using the `/smpc/queue` GET request, which is described below.

#### /smpc/queue **[GET]**
>Check the status and/or result of a specified computation request.

The status of an ongoing computation request can be accessed through the `/smpc/queue` GET request by specifying its id.

The only parameter this GET request accepts is the id of the desired computation request, as shown below.
* `request` <span style="color:red">_required_</span> A string id identifying the computation request as it was provided by the response of `/smpc/count` or `/smpc/decision_tree` POST requests.

##### Server's response

The server responds with the specified computation's status, and possibly with its current computation step, or the final computation result, in the event that the computation ended successfully. 

The response is a JSON object containing the specified computation's status, and possibly its current step or result which is too a JSON object. The server's response has the following structure.
* `status` <span style="color:red">_required_</span> A string indicating the computation's status. One of `[running, succeeded, failed, notstarted]`.
* `step` <span style="color:blue">_optional_</span> A string indicating the current step of the computation. This is present in case that the computation is in the `running` state.
* `result` <span style="color:blue">_optional_</span> A JSON object with the computation's result in case its status is `succeeded`.
The JSON object contains a single key namely `data` with the computation result.

###### Response for /smpc/count

The result for a count computation is a list with tuples of `label`, `value`, `mesh` corresponding to the appropriate counts.

```json
{
    "status": "succeeded",
    "result": {
        "data": [
            {
                "mesh": "M01.060.703",
                "value": 0,
                "label": "Infant"
            },
            {
                "mesh": "M01.060.057",
                "value": 63,
                "label": "Adolescent"
            },
            {
                "mesh": "M01.060.116",
                "value": 9936,
                "label": "Adult"
            },
            {
                "mesh": "M01.060.406",
                "value": 0,
                "label": "Child"
            }
        ]
    }
}
```

The `result` JSON object has the following structure:
* `data` <span style="color:red">_required_</span> A list of JSON objects each one corresponding to a count. Each such object has the following keys.
    * `label` <span style="color:red">_required_</span> A string, the value name corresponding to that count. Can be a tuple, triple etc. depending on the number of queried Mesh terms.
    * `value` <span style="color:red">_required_</span> An integer, the actual count for that value.
    * `mesh` <span style="color:red">_required_</span> The MeSH code of that attribute.


###### Response for /smpc/decision_tree

The result for a decision tree building is a JSON object which is a serialization of the classification tree. The JSON keys represent the test nodes and their values represent the corresponding subtrees.

Two example responses originated from different decision tree trainings can be found below.


> Tree generated with the ID3 algorithm

```json
{
    "status": "succeeded",
    "result": {
        "Patient Age == [39.67, 61.33)": {
            "Height (cm) == [153.34, 176.67)": {
                "Weight (kg) == [80.00, 100.00)": "non-diabetic",
                "Weight (kg) == [60.00, 80.00)": {
                    "Gender == female": "non-diabetic",
                    "Gender == male": "diabetic"
                },
                "Weight (kg) == [40.00, 60.00)": "non-diabetic"
            },
            "Height (cm) == [130.01, 153.34)": "non-diabetic",
            "Height (cm) == [176.67, 200.00)": "non-diabetic"
        },
        "Patient Age == [18.00, 39.67)": {
            "Weight (kg) == [80.00, 100.00)": "non-diabetic",
            "Weight (kg) == [60.00, 80.00)": {
                "Gender == female": {
                    "Height (cm) == [153.34, 176.67)": "non-diabetic",
                    "Height (cm) == [130.01, 153.34)": "diabetic",
                    "Height (cm) == [176.67, 200.00)": "non-diabetic"
                },
                "Gender == male": "non-diabetic"
            },
            "Weight (kg) == [40.00, 60.00)": "non-diabetic"
        },
        "Patient Age == [61.33, 83.00)": {
            "Weight (kg) == [80.00, 100.00)": {
                "Height (cm) == [153.34, 176.67)": "non-diabetic",
                "Height (cm) == [130.01, 153.34)": "non-diabetic",
                "Height (cm) == [176.67, 200.00)": "diabetic"
            },
            "Weight (kg) == [60.00, 80.00)": {
                "Height (cm) == [153.34, 176.67)": "diabetic",
                "Height (cm) == [130.01, 153.34)": "non-diabetic",
                "Height (cm) == [176.67, 200.00)": "non-diabetic"
            },
            "Weight (kg) == [40.00, 60.00)": "diabetic"
        }
    }
}
```
> Tree generated with the C4.5 algorithm

```json
{
    "status": "succeeded",
    "result": {
        "Patient Age > 51.50": {
            "Weight (kg) > 89.64": "diabetic",
            "Weight (kg) <= 89.64": {
                "Height (cm) > 138.23": "non-diabetic",
                "Height (cm) <= 138.23": "diabetic"
            }
        },
        "Patient Age <= 51.50": {
            "Weight (kg) > 61.33": {
                "Height (cm) > 167.22": "non-diabetic",
                "Height (cm) <= 167.22": {
                    "Gender == female": "non-diabetic",
                    "Gender == male": "diabetic"
                }
            },
            "Weight (kg) <= 61.33": "non-diabetic"
        }
    }
}
```






