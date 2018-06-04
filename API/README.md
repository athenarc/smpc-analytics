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
  "location": "/smpc/queue?request=1"
}
```
In order to check for the secure count computation's status, and/or retrieve the result you should periodically poll the above location using the `/smpc/queue` GET request, which is described below.

#### /smpc/queue **[GET]**
>Check the status and/or result of a specified computation request.

The status of an ongoing computation request can be accessed through the `/smpc/queue` GET request by specifying its id.

The only parameter this GET request accepts is the id of the desired computation request, as shown below.
* `request` <span style="color:red">_required_</span> An integer identifying the computation request as it was provided by the response of `/smpc/count` POST request.

##### Server's response

The server responds with the specified computation's status, and possibly with its current computation step, or the final computation result, in the event that the computation ended successfully. The result for a count computation is a list with pairs of `label`, `value` corresponding to the appropriate counts.

```json
{
    "status": "succeeded",
    "result": {
        "data": [
            {
                "value": 0,
                "label": "Infant"
            },
            {
                "value": 63,
                "label": "Adolescent"
            },
            {
                "value": 9936,
                "label": "Adult"
            },
            {
                "value": 0,
                "label": "Child"
            }
        ]
    }
}
```
The response is a JSON object containing the specified computation's status, and possibly its current step or result which is too a JSON object. The server's response has the following structure.

* `status` <span style="color:red">_required_</span> A string indicating the computation's status. One of `[running, succeeded, failed, notstarted]`.
* `step` <span style="color:blue">_optional_</span> A string indicating the current step of the computation. This is present in case that the computation is in the `running` state.
* `result` <span style="color:blue">_optional_</span> A JSON object with the computation's result in case its status is `succeeded`.
The JSON object contains a single key namely `data` with the computation result.
    * `data` <span style="color:red">_required_</span> A list of JSON objects each one corresponding to a count. Each such object has the following keys.
        * `label` A string, the value name corresponding to that count. Can be a tuple, triple etc. depending on the number of queried Mesh terms.
        * `value` An integer, the actual count for that value.

___
<!-- ### MHMD Driver
The MHMD Driver located on each hospital’s premises should support a RESTful API with current functionality the secure data importing into the SMPC cluster.  
#### /smpc/import **[POST]**
>Securely import data into the SMPC Platform.


The secure importing of a dataset into the SMPC cluster is initiated with the `/smpc/import` POST request.

The request's body contains a list of the desired attributes / Mesh term ids for which data should be imported into he SMPC cluster. An example request body can be found below.
```json
{
    "attributes": [
        "M01.060"
    ]
}
```
The request body is a JSON string with the single following key:
* `attributes`<span style="color:red">_required_</span> A list of the Mesh term ids for which data will be securely imported. -->
