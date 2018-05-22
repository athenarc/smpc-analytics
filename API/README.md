## SMPC API
### SMPC Server
The SMPC Server interacts with the SMPC cluster. One can pose queries to the server and get answers resulting from the SMPC computation. For this purpose, the server provides the following RESTful API.

#### /smpc/count **[POST]**
>Initiate a secure count computation on a specified attribute.

You can get the securely computed counts for a specified Mesh term.

Through the request's body, one can specify the desired Mesh term. The values the count of which will be computed are the children of the specified Mesh term from the Mesh ontology. For example, if a user specifies that she wants the counts for the Mesh term _Age Groups_ `[M01.060]` , she will get 4 counts back corresponding to the four children of _Age Groups_, namely _Adolescent_ `[M01.060.057]`, _Adult_`[M01.060.116]`, _Child_`[M01.060.406]` and _Infant_`[M01.060.703]`.

An example of the requests body can be found below.

```json
{
    "attribute": "Persons",
    "datasources": [
      "HospitalA",
      "HospitalB"
    ]
}
```
The request is a JSON string consisting of the following parameters.
* `attribute` <span style="color:red">_required_</span> The name of the Mesh term for which the counts should be computed
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
* `request` <span style="color:red">_required_</span> An integer identifying the computation request as it was provided by the response of `/smpc/histogram` POST request.

##### Server's response

The server responds with the specified computation's status, and possibly with its current computation step, or the final computation result, in the event that the computation ended successfully. The result for a count computation is a list with pairs of `label`, `value` corresponding to the appropriate counts.

```json
{
    "status": "succeeded",
    "result": {
        "data": [
            {
                "value": 0,
                "label": "Prisoners"
            },
            {
                "value": 0,
                "label": "Vegetarians"
            },
            {
                "value": 0,
                "label": "Transients and Migrants"
            },
            {
                "value": 10,
                "label": "Men"
            },
            {
                "value": 0,
                "label": "Students"
            },
            {
                "value": 0,
                "label": "Child, Abandoned"
            },
            {
                "value": 0,
                "label": "Transplant Recipients"
            },
            {
                "value": 0,
                "label": "Tissue Donors"
            },
            {
                "value": 0,
                "label": "Refugees"
            },
            {
                "value": 0,
                "label": "Spouses"
            },
            {
                "value": 0,
                "label": "Pedestrians"
            },
            {
                "value": 0,
                "label": "Child, Exceptional"
            },
            {
                "value": 0,
                "label": "Minors"
            },
            {
                "value": 0,
                "label": "Parents"
            },
            {
                "value": 0,
                "label": "Emigrants and Immigrants"
            },
            {
                "value": 0,
                "label": "Consultants"
            },
            {
                "value": 0,
                "label": "Child, Foster"
            },
            {
                "value": 0,
                "label": "Siblings"
            },
            {
                "value": 0,
                "label": "Veterans"
            },
            {
                "value": 0,
                "label": "Drug Users"
            },
            {
                "value": 0,
                "label": "Sexual and Gender Minorities"
            },
            {
                "value": 0,
                "label": "Sex Workers"
            },
            {
                "value": 0,
                "label": "Child, Unwanted"
            },
            {
                "value": 0,
                "label": "Jehovah's Witnesses"
            },
            {
                "value": 0,
                "label": "Homebound Persons"
            },
            {
                "value": 0,
                "label": "Occupational Groups"
            },
            {
                "value": 0,
                "label": "Famous Persons"
            },
            {
                "value": 0,
                "label": "Legal Guardians"
            },
            {
                "value": 0,
                "label": "Terminally Ill"
            },
            {
                "value": 0,
                "label": "Patients"
            },
            {
                "value": 0,
                "label": "Homeless Persons"
            },
            {
                "value": 0,
                "label": "Visitors to Patients"
            },
            {
                "value": 0,
                "label": "Slaves"
            },
            {
                "value": 0,
                "label": "Smokers"
            },
            {
                "value": 0,
                "label": "Bedridden Persons"
            },
            {
                "value": 0,
                "label": "Athletes"
            },
            {
                "value": 0,
                "label": "Vulnerable Populations"
            },
            {
                "value": 0,
                "label": "Abortion Applicants"
            },
            {
                "value": 0,
                "label": "Adult Children"
            },
            {
                "value": 0,
                "label": "Crime Victims"
            },
            {
                "value": 9,
                "label": "Women"
            },
            {
                "value": 0,
                "label": "Single Person"
            },
            {
                "value": 0,
                "label": "Missionaries"
            },
            {
                "value": 0,
                "label": "Caregivers"
            },
            {
                "value": 0,
                "label": "Volunteers"
            },
            {
                "value": 0,
                "label": "Criminals"
            },
            {
                "value": 0,
                "label": "Survivors"
            },
            {
                "value": 0,
                "label": "Working Poor"
            },
            {
                "value": 0,
                "label": "Medically Uninsured"
            },
            {
                "value": 0,
                "label": "Disabled Persons"
            },
            {
                "value": 0,
                "label": "Disaster Victims"
            },
            {
                "value": 0,
                "label": "Mentors"
            },
            {
                "value": 0,
                "label": "Friends"
            },
            {
                "value": 0,
                "label": "Child of Impaired Parents"
            },
            {
                "value": 0,
                "label": "Sexual Partners"
            },
            {
                "value": 0,
                "label": "Population Groups"
            },
            {
                "value": 0,
                "label": "Age Groups"
            },
            {
                "value": 0,
                "label": "Research Subjects"
            },
            {
                "value": 0,
                "label": "Alcoholics"
            },
            {
                "value": 0,
                "label": "Grandparents"
            },
            {
                "value": 0,
                "label": "Multiple Birth Offspring"
            },
            {
                "value": 0,
                "label": "Child, Orphaned"
            },
            {
                "value": 0,
                "label": "Child, Adopted"
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
        * `label` A string, the value name corresponding to that count.
        * `value` An integer, the actual count for that value.

___
### MHMD Driver
The MHMD Driver located on each hospital’s premises should support a RESTful API with current functionality the secure data importing into the SMPC cluster.  
#### /smpc/import **[POST]**
>Securely import data into the SMPC Platform.

The secure importing of a dataset into the SMPC cluster is initiated with the `/smpc/import` POST request.

The request's body contains the desired attribute / Mesh term for which data should be imported into the SMPC cluster. An example request body can be found below.
```json
{
  "attribute": "Persons"
}
```
The request body is a JSON string with the single following key:
* `attribute`<span style="color:red">_required_</span> The Mesh term for which data will be securely imported.
