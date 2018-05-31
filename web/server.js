var SIMULATION_MODE = false;
process.argv.forEach(function (val, index, array) {
    if (val == '-sim' || val == '--sim' || val == '-simulation' || val == '--simulation') {
        SIMULATION_MODE = true;
    }
});

if (SIMULATION_MODE) {
    console.log('\n[NODE] Running in simulation mode\n');
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


app.get('/smpc/queue', function(req, res) {
    request = req.query.request;
    db.get(request)
    .then((value) => {
        res.send(value);
    }).catch((err) => {
        console.log(err);
        res.send(JSON.stringify({'status':'notstarted'}));
    });
});


function pipeline(req_counter, content, parent, computation_type) {
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
        db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code generated. Now compiling.'}))
        .catch((err) => {
            console.log(err);
        });
        if (computation_type == 'count' || computation_type == 'histogram') {
            return _unlinkIfExists(parent + '/histogram/.main' + req_counter + '.sb.src');
        } else if (computation_type == 'id3'){
            return _unlinkIfExists(parent + '/ID3/.main' + req_counter + '.sb.src');
        }
    }).then((msg) => {
        if (SIMULATION_MODE) {
            console.log("[NODE] Old .histogram_main" + req_counter + ".sb.src deleted.\n");
            if (computation_type == 'count' || computation_type == 'histogram') {
                return _exec('sharemind-scripts/compile.sh histogram/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
            } else if(computation_type == 'id3'){
                return _exec('sharemind-scripts/compile.sh ID3/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
            }
        } else {
            console.log("[NODE] Old .histogram_main" + req_counter + ".sb.src deleted.\n");
            if (computation_type == 'count' || computation_type == 'histogram') {
                return _exec('sharemind-scripts/sm_compile_and_run.sh histogram/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
            } else if(computation_type == 'id3'){
                return _exec('sharemind-scripts/sm_compile_and_run.sh ID3/main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
            }
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled. Now running.'}))
            .catch((err) => {
                console.log(err);
            });
            console.log('[NODE] Request(' + req_counter + ') Program compiled.\n');
            if (computation_type == 'count' || computation_type == 'histogram') {
                return _exec('sharemind-scripts/run.sh histogram/main' + req_counter + '.sb 2> out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
            } else if(computation_type == 'id3'){
                return _exec('sharemind-scripts/run.sh ID3/main' + req_counter + '.sb 2> out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
            }
        } else {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code compiled and run. Now generating output.'}))
            .catch((err) => {
                console.log(err);
            });
            console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
            return _exec('tail -n +`cut -d " "  -f "9-" /etc/sharemind/server.log  | grep -n "Starting process" | tail -n 1 | cut -d ":" -f 1` /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(req_counter, JSON.stringify({'status':'running', 'step':'SecreC code run. Now generating output.'}))
            .catch((err) => {
                console.log(err);
            });
        }
        console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
        if (computation_type == 'count') {
            return _exec('python web/response.py out_' + req_counter + '.txt | python web/transform_response.py  configuration_' + req_counter + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json' , {cwd: parent});
        } else if (computation_type == 'histogram') {
            return _exec('python web/response.py out_' + req_counter + '.txt', {cwd: parent});
        } else if (computation_type == 'id3') {
            return _exec('python web/id3_response.py out_' + req_counter + '.txt', {cwd: parent});
        }
    }).then((result) => {
        console.log('[NODE] Request(' + req_counter + ') Response ready.\n');
        var result_obj = {'status':'succeeded','result': ''};
        result_obj.result = JSON.parse(result);
        db.put(req_counter, JSON.stringify(result_obj))
        .catch((err) => {
            console.log(err);
        });
        return;
    }).catch((err) => {
        db.put(req_counter, JSON.stringify({'status':'failed'}))
        .catch((err) => {
            console.log(err);
        });
        console.log(err);
    });
}

app.post('/smpc/histogram', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;
    res.status(202).json({"location" : "/smpc/queue?request="+req_counter});
    db.put(req_counter, JSON.stringify({'status':'running'}))
    .then((buffer) => {
        pipeline(req_counter, content, parent, 'histogram');
    }).catch((err) => {
        console.log(err);
    });
});


app.post('/smpc/count', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;
    var mhmdDNS = JSON.parse(fs.readFileSync('MHMDdns.json', 'utf8'));
    for (let datasrc of datasources) {        // Check that all IPs exist
        if ((datasrc in mhmdDNS) == false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find IP for ' + datasrc + ', it does not exist in MHMDdns.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }
    // since no error occured in the above loop, we have all IPs
    res.status(202).json({"location" : "/smpc/queue?request="+req_counter});
    db.put(req_counter, JSON.stringify({'status':'running', 'step' : 'Securely importing data'}));

    // // send the requests for import
    var import_promises = [];
    for (let datasrc of datasources) {
        import_promises.push(_sendRequest(datasrc, mhmdDNS, attributes));
    }
    // wait them all to finish
    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
    }).then((buffer) => {
        pipeline(req_counter, content, parent, 'count');
    }).catch((err) => {
        console.log(err);
    });
});

app.post('/smpc/id3', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;
    var attributes = req.body.attributes;
    var class_attribute = req.body.class_attribute;
    var datasources = req.body.datasources;
    attributes.push(class_attribute);
    var mhmdDNS = JSON.parse(fs.readFileSync('MHMDdns.json', 'utf8'));
    for (let datasrc of datasources) {        // Check that all IPs exist
        if ((datasrc in mhmdDNS) == false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find IP for ' + datasrc + ', it does not exist in MHMDdns.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }
    // since no error occured in the above loop, we have all IPs
    res.status(202).json({"location" : "/smpc/queue?request="+req_counter});
    db.put(req_counter, JSON.stringify({'status':'running', 'step' : 'Securely importing data'}));

    // // send the requests for import
    var import_promises = [];
    for (let datasrc of datasources) {
        import_promises.push(_sendRequest(datasrc, mhmdDNS, attributes));
    }
    // wait them all to finish
    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
    }).then((buffer) => {
        pipeline(req_counter, content, parent, 'id3');
    }).catch((err) => {
        console.log(err);
    });
});


app.post('/histogram', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;

    _writeFile(parent+'/configuration_' + req_counter + '.json', content, 'utf8')
    .then((buffer) => {
        console.log('[NODE] Request(' + req_counter + ') Configuration file was saved.\n');
        return _exec('python dataset-scripts/main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('[NODE] Request(' + req_counter + ') Main generated.\n');
        return _unlinkIfExists(parent + '/histogram/.histogram_main_' + req_counter + '.sb.src');
    }).then((msg) => {
        if (SIMULATION_MODE) {
            console.log("[NODE] Old .histogram_main" + req_counter + ".sb.src deleted.\n");
            return _exec('sharemind-scripts/compile.sh histogram/histogram_main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
        } else {
            console.log("[NODE] Old .histogram_main" + req_counter + ".sb.src deleted.\n");
            return _exec('sharemind-scripts/sm_compile_and_run.sh histogram/histogram_main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            console.log('[NODE] Request(' + req_counter + ') Program compiled.\n');
            return _exec('sharemind-scripts/run.sh histogram/histogram_main_' + req_counter + '.sb 2> web/out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        } else {
            console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
            return _exec('tail -n +`cut -d " "  -f "9-" /etc/sharemind/server.log  | grep -n "Starting process" | tail -n 1 | cut -d ":" -f 1` /etc/sharemind/server.log | cut -d " "  -f "9-" >  web/out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
        return _exec('python plot.py ' + req_counter);
    }).then((result) => {
        console.log('[NODE] Request(' + req_counter + ') Plotting done.\n');
        var graph_name = result.toString();
        graph_name = graph_name.slice(0,-1);
        console.log('[NODE]' + graph_name);
        res.send(graph_name);
    }).catch((err) => {
        console.log(err);
    });
});

const port = 3000;
app.listen(port, () => console.log('Example app listening on port ' + port + '!'));

const FgRed = "\x1b[31m";
const FgGreen = "\x1b[32m";
const ResetColor = "\x1b[0m";
