var SIMULATION_MODE = false;
process.argv.forEach(function (val, index, array) {
    if (val == '-sim' || val == '--sim' || val == '-simulation' || val == '--simulation') {
        SIMULATION_MODE = true;
    }
});

if (SIMULATION_MODE) {
    console.log('\n[NODE SIMULATION] Running in simulation mode\n');
} else {
    console.log('\n[NODE] Running in Secure Multiparty Computation mode with 3 servers\n');
}

const express = require('express');
const app = express();
const { exec } = require('child_process');
const fs = require('fs');
var path = require('path');
var bodyParser = require('body-parser');
var parse = require('csv-parse');
var rp = require('request-promise');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
var frontend = __dirname + "/frontend/";
var visuals = __dirname + "/visuals/";
global.__basedir = __dirname;

var level = require('level');

var db = level('./mydb');


app.get('/', function (req, res) {
    res.sendFile(path.join(frontend + 'index.html'));
});

app.use(express.static(path.join(__dirname, 'frontend'))); // public/static files
app.use("/visuals", express.static(__dirname + '/visuals'));

var req_counter = 0; // count the requests and give each new request a new ID

// function to return a promise to write to file
function _writeFile(filename, content, encoding = null) {
    return new Promise((resolve, reject) => {
      try {
          fs.writeFile(filename, content, encoding, (err, buffer) => {
            if (err) {
                reject(err);
            } else {
                resolve(buffer);
            }
          });
      } catch (err) {
          reject(err);
      }
    });
}

// function to return a promise to exec a process
function _exec(script, args) {
    return new Promise((resolve, reject) => {
      try {
          exec(script, args, (err, buffer) => {
            if (err) {
                reject(err);
            } else {
                resolve(buffer);
            }
          });
      } catch (err) {
          reject(err);
      }
    });
}

// function to return a promise to unlink a file if exists
function _unlinkIfExists(filename) {
    return new Promise((resolve, reject) => {
        fs.stat(filename, (err, stat) => {
            if (err === null) {
                fs.unlink(filename, err => {
                    if (err) { return reject(err); }
                    resolve(`Removing document at ${path}`);
                });
            } else if (err.code === 'ENOENT') {
                resolve('File does not exist');
            }
        });
    });
}

// function to return a promise to send request for import
function _sendRequest(datasrc, mhmdDNS, attributes) {
    var uri = mhmdDNS[datasrc];
    var options = {                       // Configure the request
        method: 'POST',
        uri: 'http://' + uri + '/smpc/import',
        body: {
            "attributes": attributes,
            "datasource": datasrc
        },
        json: true                        // Automatically stringifies the body to JSON
    };

    console.log(FgGreen + 'Request for import sent to: ' + datasrc + ' at ' + uri + ResetColor);
    return rp(options);                   // Return promise to start the request
}

// function to send requests for import and return array of promises
function import_from_servers(req, res, req_counter, computation_type) {
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;
    if (computation_type == 'id3') {
        var class_attribute = req.body.class_attribute;
        attributes.push(class_attribute);
    }
    var mhmdDNS = JSON.parse(fs.readFileSync('MHMDdns.json', 'utf8'));
    for (let datasrc of datasources) {        // Check that all IPs exist
        if ((datasrc in mhmdDNS) == false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find IP for ' + datasrc + ', it does not exist in MHMDdns.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }
    // since no error occured in the above loop, we have all IPs
    db.put(req_counter, JSON.stringify({'status':'running', 'step' : 'Securely importing data'}));

    // // send the requests for import
    var import_promises = [];
    for (let datasrc of datasources) {
        import_promises.push(_sendRequest(datasrc, mhmdDNS, attributes));
    }
    // return array of promises for import
    return import_promises;
}


// function to import local data and return promise
function import_locally(attributes, datasources, res, parent, req_counter) {
    var localDNS = JSON.parse(fs.readFileSync('localDNS.json', 'utf8'));
    for (let datasrc of datasources) {        // Check that all IPs exist
        if ((datasrc in localDNS) == false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find path for ' + datasrc + ', it does not exist in localDNS.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }

    // exec asynch python simulated imports
    var import_promises = [];
    for (let datasrc of datasources) {
        var dataset = localDNS[datasrc];
        console.log('[NODE SIMULATION] Request(' + req_counter + ') python ./dataset-scripts/simulated_import.py ' + dataset + ' --attributes "' + attributes.join(';') + '" --table ' + datasrc + '\n');

        import_promises.push( _exec('python ./dataset-scripts/simulated_import.py ' + dataset + ' --attributes "' + attributes.join(';') + '" --table ' + datasrc, {stdio:[0,1,2],cwd: parent}) );
    }
    // return array of promises for import
    return import_promises;
}


app.get('/smpc/queue', function(req, res) {
    request = req.query.request;
    db.get(request)
    .then((value) => {
        res.send(value);
    }).catch((err) => {
        console.log(FgRed + '[NODE] ' + ResetColor + err);
        res.send(JSON.stringify({'status':'notstarted'}));
    });
});


function pipeline(req_counter, content, parent, computation_type, plot) {
    _writeFile(parent+'/configuration_' + req_counter + '.json', content, 'utf8')
    .then((buffer) => {
        console.log('[NODE] Request(' + req_counter + ') Configuration file was saved.\n');
        if (computation_type == 'count') {
            return _exec('python dataset-scripts/count_main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        } else if (computation_type == 'histogram') {
            return _exec('python dataset-scripts/main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        } else if (computation_type == 'id3') {
            return _exec('python dataset-scripts/id3_main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        console.log('[NODE] Request(' + req_counter + ') Main generated.\n');
        db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code generated. Now compiling and running.'})).catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        if (computation_type == 'count' || computation_type == 'histogram') {
            return _unlinkIfExists(parent + '/histogram/.main_' + req_counter + '.sb.src');
        } else if (computation_type == 'id3'){
            return _unlinkIfExists(parent + '/ID3/.main_' + req_counter + '.sb.src');
        }
    }).then((msg) => {
        console.log("[NODE] Old .main_" + req_counter + ".sb.src deleted.\n");
        if (computation_type == 'count' || computation_type == 'histogram') {
            return _exec('sharemind-scripts/sm_compile_and_run.sh histogram/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
        } else if(computation_type == 'id3'){
            return _exec('sharemind-scripts/sm_compile_and_run.sh ID3/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled and run. Now generating output.'})).catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
        return _exec('tail -n +`cut -d " "  -f "9-" /etc/sharemind/server.log  | grep -n "Starting process" | tail -n 1 | cut -d ":" -f 1` /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
        if (computation_type == 'count') {
            return _exec('python web/response.py out_' + req_counter + '.txt | python web/transform_response.py  configuration_' + req_counter + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json' , {cwd: parent});
        } else if (computation_type == 'histogram') {
            return _exec('python web/response.py out_' + req_counter + '.txt', {cwd: parent});
        } else if (computation_type == 'id3') {
            return _exec('python web/id3_response.py out_' + req_counter + '.json configuration_' + req_counter + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {cwd: parent});
        }
    }).then((result) => {
        console.log('[NODE] Request(' + req_counter + ') Response ready.\n');
        var result_obj = {'status':'succeeded','result': ''};
        result_obj.result = JSON.parse(result);
        db.put(req_counter, JSON.stringify(result_obj)).catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        return;
    }).catch((err) => {
        db.put(req_counter, JSON.stringify({'status':'failed'}))
        .catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        console.log(FgRed + '[NODE] ' + ResetColor + err);
    });
}


function pipeline_simulation(req_counter, content, parent, computation_type, plot) {
    _writeFile(parent+'/configuration_' + req_counter + '.json', content, 'utf8')
    .then((buffer) => {
        console.log('[NODE SIMULATION] Request(' + req_counter + ') Configuration file was saved.\n');
        if (computation_type == 'count') {
            return _exec('python dataset-scripts/count_main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        } else if (computation_type == 'histogram') {
            return _exec('python dataset-scripts/main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        } else if (computation_type == 'id3') {
            return _exec('python dataset-scripts/id3_main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        console.log('[NODE SIMULATION] Request(' + req_counter + ') Main generated.\n');
        db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code generated. Now compiling.'})).catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        if (computation_type == 'count' || computation_type == 'histogram') {
            return _unlinkIfExists(parent + '/histogram/.main_' + req_counter + '.sb.src');
        } else if (computation_type == 'id3'){
            return _unlinkIfExists(parent + '/ID3/.main_' + req_counter + '.sb.src');
        }
    }).then((msg) => {
        console.log("[NODE SIMULATION] Old .main_" + req_counter + ".sb.src deleted.\n");
        if (computation_type == 'count' || computation_type == 'histogram') {
            return _exec('sharemind-scripts/compile.sh histogram/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
        } else if(computation_type == 'id3'){
            return _exec('sharemind-scripts/compile.sh ID3/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled. Now running.'})).catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        console.log('[NODE SIMULATION] Request(' + req_counter + ') Program compiled.\n');
        if (computation_type == 'count' || computation_type == 'histogram') {
            return _exec('sharemind-scripts/run.sh histogram/main_' + req_counter + '.sb 2> out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        } else if(computation_type == 'id3'){
            return _exec('sharemind-scripts/run.sh ID3/main_' + req_counter + '.sb  2>&1 >/dev/null | sed --expression="s/,  }/ }/g" > id3_out_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code run. Now generating output.'})).catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        console.log('[NODE SIMULATION] Request(' + req_counter + ') Program executed.\n');
        if (computation_type == 'count') {
            return _exec('python web/response.py out_' + req_counter + '.txt | python web/transform_response.py  configuration_' + req_counter + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json' , {cwd: parent});
        } else if (computation_type == 'histogram') {
            return _exec('python web/response.py out_' + req_counter + '.txt', {cwd: parent});
        } else if (computation_type == 'id3') {
            return _exec('python web/id3_response.py out_' + req_counter + '.json configuration_' + req_counter + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {cwd: parent});
        }
    }).then((result) => {
        console.log('[NODE SIMULATION] Request(' + req_counter + ') Response ready.\n');
        var result_obj = {'status':'succeeded','result': ''};
        result_obj.result = JSON.parse(result);
        db.put(req_counter, JSON.stringify(result_obj)).catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        return;
    }).catch((err) => {
        db.put(req_counter, JSON.stringify({'status':'failed'}))
        .catch((err) => {
            console.log(FgRed + '[NODE] ' + ResetColor + err);
        });
        console.log(FgRed + '[NODE] ' + ResetColor + err);
    });
}



app.post('/smpc/histogram', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;

    var plot = (typeof req.body.plot !== 'undefined' && req.body.plot); // if plot exists in req.body
    if (!plot) {
        res.status(202).json({"location" : "/smpc/queue?request="+req_counter});
    }
    var import_promises = [];
    if (SIMULATION_MODE) {
        // create list of attribute names from the POST request
        var attributes_lst = [];
        for (var i = 0; i < attributes.length; i++) {
            for (var j = 0; j < attributes[i].length; j++) {
                attributes_lst.push(attributes[i][j].name);
            }
        }
        // TODO: Change column indexes to column names.
        import_promises = import_locally(attributes_lst, datasources, res, parent, req_counter);
    } else {

      // TODO: Importing with servers !!

    }
    var print_msg = (SIMULATION_MODE) ? 'NODE SIMULATION' : 'NODE';

    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
        return db.put(req_counter, JSON.stringify({'status':'running'}));
    }).then((buffer) => {
        return _writeFile(parent+'/configuration_' + req_counter + '.json', content, 'utf8');
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + req_counter + ') Configuration file was saved.\n');
        return _exec('python dataset-scripts/main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + req_counter + ') Main generated.\n');
        var db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
        db.put(req_counter, JSON.stringify({'status':'running', 'step':db_msg})).catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        return _unlinkIfExists(parent + '/histogram/.main_' + req_counter + '.sb.src');
    }).then((msg) => {
        console.log('['+print_msg+'] Old .main_' + req_counter + '.sb.src deleted.\n');
        var exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh histogram/main_' : 'sharemind-scripts/sm_compile_and_run.sh histogram/main_';
        return _exec(exec_arg + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled. Now running.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + req_counter + ') Program compiled.\n');
            return _exec('sharemind-scripts/run.sh histogram/main_' + req_counter + '.sb 2> out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        } else {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled and run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
            return _exec('tail -n +`cut -d " "  -f "9-" /etc/sharemind/server.log  | grep -n "Starting process" | tail -n 1 | cut -d ":" -f 1` /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + req_counter + ') Program executed.\n');
        }

        if (plot) {
            return _exec('python plot.py ' + req_counter);
        } else {
            return _exec('python web/response.py out_' + req_counter + '.txt', {cwd: parent});
        }
    }).then((result) => {
        if (plot) {
            console.log('['+print_msg+'] Request(' + req_counter + ') Plotting done.\n');
            var graph_name = result.toString();
            graph_name = graph_name.slice(0,-1);
            console.log('['+print_msg+']' + graph_name);
            res.send(graph_name);
        } else {
            console.log('['+print_msg+'] Request(' + req_counter + ') Response ready.\n');
            var result_obj = {'status':'succeeded','result': ''};
            result_obj.result = JSON.parse(result);
            db.put(req_counter, JSON.stringify(result_obj)).catch((err) => {
              console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
            });
        }
        return ;
    }).catch((err) => {
        db.put(req_counter, JSON.stringify({'status':'failed'}))
        .catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
    });
});


app.post('/smpc/count', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;

    var plot = ('plot' in req.body); // if plot exists in req.body
    if (!plot) {
        res.status(202).json({"location" : "/smpc/queue?request="+req_counter});
    }
    // create array of requests for import
    var import_promises = [];
    if (SIMULATION_MODE) {
        //TODO: Generate csv from Json before importing.
        import_promises = import_locally(attributes, datasources, res, parent, req_counter);
    } else {
        import_promises = import_from_servers(req, res, req_counter, 'count');
    }

    var print_msg = (SIMULATION_MODE) ? 'NODE SIMULATION' : 'NODE';
    // wait them all to finish
    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
        return db.put(req_counter, JSON.stringify({'status':'running'}));
    }).then((buffer) => {
        return _writeFile(parent+'/configuration_' + req_counter + '.json', content, 'utf8');
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + req_counter + ') Configuration file was saved.\n');
        return _exec('python dataset-scripts/count_main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + req_counter + ') Main generated.\n');
        var db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
        db.put(req_counter, JSON.stringify({'status':'running', 'step':db_msg})).catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        return _unlinkIfExists(parent + '/histogram/.main_' + req_counter + '.sb.src');
    }).then((msg) => {
        console.log('['+print_msg+'] Old .main_' + req_counter + '.sb.src deleted.\n');
        var exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh histogram/main_' : 'sharemind-scripts/sm_compile_and_run.sh histogram/main_';
        return _exec(exec_arg + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled. Now running.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + req_counter + ') Program compiled.\n');
            return _exec('sharemind-scripts/run.sh histogram/main_' + req_counter + '.sb 2> out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        } else {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled and run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
            return _exec('tail -n +`cut -d " "  -f "9-" /etc/sharemind/server.log  | grep -n "Starting process" | tail -n 1 | cut -d ":" -f 1` /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + req_counter + ') Program executed.\n');
        }

        if (plot) {
            // TODO: New plotting for count!! below is the one for histograms...

            // return _exec('python plot.py ' + req_counter);
        } else {
            return _exec('python web/response.py out_' + req_counter + '.txt | python web/transform_response.py  configuration_' + req_counter + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json' , {cwd: parent});
        }
    }).then((result) => {
        if (plot) {

            // TODO: New plotting for count!! below is the one for histograms...

            // console.log('['+print_msg+'] Request(' + req_counter + ') Plotting done.\n');
            // var graph_name = result.toString();
            // graph_name = graph_name.slice(0,-1);
            // console.log('['+print_msg+']' + graph_name);
            // res.send(graph_name);
        } else {
            console.log('['+print_msg+'] Request(' + req_counter + ') Response ready.\n');
            var result_obj = {'status':'succeeded','result': ''};
            result_obj.result = JSON.parse(result);
            db.put(req_counter, JSON.stringify(result_obj)).catch((err) => {
              console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
            });
        }
        return ;
    }).catch((err) => {
        db.put(req_counter, JSON.stringify({'status':'failed'}))
        .catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
    });
});

app.post('/smpc/id3', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;
    var plot = (typeof req.body.plot !== 'undefined' && req.body.plot); // if plot exists in req.body
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;
    var class_attribute = req.body.class_attribute;
    attributes.push(class_attribute);

    // create array of requests for import
    var import_promises = [];
    if (SIMULATION_MODE) {
        //TODO: Generate csv from Json before importing.
        import_promises = import_locally(attributes, datasources, res, parent, req_counter);
    } else {
        import_promises = import_from_servers(req, res, req_counter, 'id3');
    }

    // wait them all to finish
    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            pipeline_simulation(req_counter, content, parent, 'id3', plot);
        } else {
            pipeline(req_counter, content, parent, 'id3', plot);
        }
    }).catch((err) => {
        console.log(FgRed + '[NODE] ' + ResetColor + err);
    });
});



const port = 3000;
app.listen(port, () => console.log('Example app listening on port ' + port + '!'));

const FgRed = "\x1b[31m";
const FgGreen = "\x1b[32m";
const ResetColor = "\x1b[0m";
