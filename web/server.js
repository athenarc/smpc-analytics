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
const { execSync } = require('child_process');
const fs = require('fs');
const uuidv4 = require('uuid/v4');
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
function _sendRequest(datasrc, mhmdDNS, attributes, uid, action) {
    var uri = mhmdDNS[datasrc];
    var options = {                       // Configure the request
        method: 'POST',
        uri: 'http://' + uri + action,
        body: {
            "attributes": attributes,
            "datasource": datasrc+'_'+uid
        },
        json: true                        // Automatically stringifies the body to JSON
    };

    console.log(FgGreen + 'Request for import sent to: ' + datasrc + ' at ' + uri + ResetColor);
    return rp(options);                   // Return promise to start the request
}

// function to send requests for import and return array of promises
function import_from_servers(attributes, datasources, res, parent, uid, action, DNSfile) {
    var mhmdDNS = JSON.parse(fs.readFileSync(DNSfile, 'utf8'));
    if (typeof datasources == 'undefined'){
        datasources = Object.keys(mhmdDNS);
    }
    for (let datasrc of datasources) {        // Check that all IPs exist
        if ((datasrc in mhmdDNS) == false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find IP for ' + datasrc + ', it does not exist in MHMDdns.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }
    // since no error occured in the above loop, we have all IPs
    db.put(uid, JSON.stringify({'status':'running', 'step' : 'Securely importing data'}));

    // // send the requests for import
    var import_promises = [];
    for (let datasrc of datasources) {
        import_promises.push(_sendRequest(datasrc, mhmdDNS, attributes, uid, action));
    }
    // return array of promises for import
    return import_promises;
}


// function to import local data and return promise
function import_locally(attributes, datasources, res, parent, uid, type) {
    var localDNS = JSON.parse(fs.readFileSync('localDNS.json', 'utf8'));
    if (typeof datasources == 'undefined'){
        datasources = Object.keys(localDNS);
    }
    for (let datasrc of datasources) {         // Check that all IPs exist
        if ((datasrc in localDNS) == false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find path for ' + datasrc + ', it does not exist in localDNS.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }

    if (type == 'mesh') {
        // var json_to_csv_promises = [];
        for (let datasrc of datasources) {
            var patient_file = localDNS[datasrc][type];
            var csv_file = './datasets/' + datasrc + '_' + uid + '.csv';
            localDNS[datasrc][type] = csv_file;
            console.log('NODE SIMULATION] python mhmd-driver/mesh_json_to_csv.py \"' + attributes.join(' ') + '\" '+ patient_file + ' --output ' + csv_file + ' --mtrees ./mhmd-driver/m.json --mtrees_inverted ./mhmd-driver/m_inv.json --mapping ./mhmd-driver/mesh_mapping.json\n');
            execSync('python mhmd-driver/mesh_json_to_csv.py \"' + attributes.join(' ') + '\" '+ patient_file + ' --output ' + csv_file + ' --mtrees ./mhmd-driver/m.json --mtrees_inverted ./mhmd-driver/m_inv.json --mapping ./mhmd-driver/mesh_mapping.json', {stdio:[0,1,2],cwd: parent}, (err, stdout, stderr) => {
                if (err) {
                    console.log(FgRed + '[NODE SIMULATION] ' + ResetColor + err);
                    return;
                }
            });
        }
        console.log(FgGreen + 'Json succesfully converted to CSV ' + ResetColor);
    }


    var import_promises = [];
    // exec asynch python simulated imports
    for (let datasrc of datasources) {
        var dataset = localDNS[datasrc][type];
        console.log('[NODE SIMULATION] Request(' + uid + ') python ./dataset-scripts/simulated_import.py ' + dataset + ' --attributes "' + attributes.join(';') + '" --table "' + datasrc+'_'+uid + '"\n');
        import_promises.push( _exec('python ./dataset-scripts/simulated_import.py ' + dataset + ' --attributes "' + attributes.join(';') + '" --table "' + datasrc+'_'+uid +'"', {stdio:[0,1,2],cwd: parent}) );
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



app.post('/smpc/histogram', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    var uid = uuidv4();
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;

    db.put(uid, JSON.stringify({'status':'running'}));
    var plot = ('plot' in req.body); // if plot exists in req.body
    if (!plot) {
        res.status(202).json({"location" : "/smpc/queue?request="+uid});
    }
    // create list of attribute names from the POST request
    var attributes_lst = [];
    for (var i = 0; i < attributes.length; i++) {
        for (var j = 0; j < attributes[i].length; j++) {
            attributes_lst.push(attributes[i][j].name);
        }
    }
    var import_promises = [];
    if (SIMULATION_MODE) {
        // TODO: Change column indexes to column names.
        import_promises = import_locally(attributes_lst, datasources, res, parent, uid, 'cvi');
    } else {
        import_promises = import_from_servers(attributes_lst, datasources, res, parent, uid, '/smpc/import/cvi', 'MHMDdns_cvi.json');
    }
    var print_msg = (SIMULATION_MODE) ? 'NODE SIMULATION' : 'NODE';

    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
        return _writeFile(parent+'/configuration_' + uid + '.json', content, 'utf8');
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + uid + ') Configuration file was saved.\n');
        return _exec('python dataset-scripts/main_generator.py configuration_' + uid + '.json', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + uid + ') Main generated.\n');
        var db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
        db.put(uid, JSON.stringify({'status':'running', 'step':db_msg})).catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        return _unlinkIfExists(parent + '/histogram/.main_' + uid + '.sb.src');
    }).then((msg) => {
        console.log('['+print_msg+'] Old .main_' + uid + '.sb.src deleted.\n');
        var exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh histogram/main_' : 'sharemind-scripts/sm_compile_and_run.sh histogram/main_';
        return _exec(exec_arg + uid + '.sc', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code compiled. Now running.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + uid + ') Program compiled.\n');
            return _exec('sharemind-scripts/run.sh histogram/main_' + uid + '.sb 2> out_' + uid + '.txt', {stdio:[0,1,2],cwd: parent});
        } else {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code compiled and run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE] Request(' + uid + ') Program executed.\n');
            return _exec('grep --fixed-strings --text "`grep --text "' + uid + '" /etc/sharemind/server.log | tail -n 1 | cut -d " "  -f "7-8"`" /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + uid + '.txt', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + uid + ') Program executed.\n');
        }

        if (plot) {
            return _exec('python plot.py ' + uid);
        } else {
            return _exec('python web/response.py out_' + uid + '.txt', {cwd: parent});
        }
    }).then((result) => {
        if (plot) {
            console.log('['+print_msg+'] Request(' + uid + ') Plotting done.\n');
            var graph_name = result.toString();
            graph_name = graph_name.slice(0,-1);
            console.log('['+print_msg+']' + graph_name);
            res.send(graph_name);
        } else {
            console.log('['+print_msg+'] Request(' + uid + ') Response ready.\n');
            var result_obj = {'status':'succeeded','result': ''};
            result_obj.result = JSON.parse(result);
            db.put(uid, JSON.stringify(result_obj)).catch((err) => {
              console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
            });
        }
        return ;
    }).catch((err) => {
        db.put(uid, JSON.stringify({'status':'failed'}))
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
    var uid = uuidv4();
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;

    var plot = ('plot' in req.body); // if plot exists in req.body
    db.put(uid, JSON.stringify({'status':'running'}));
    if (!plot) {
        res.status(202).json({"location" : "/smpc/queue?request="+uid});
    }
    // create array of requests for import
    var import_promises = [];
    if (SIMULATION_MODE) {
        import_promises = import_locally(attributes, datasources, res, parent, uid, 'mesh');
    } else {
        import_promises = import_from_servers(attributes, datasources, res, parent, uid, '/smpc/import', 'MHMDdns.json');
    }

    var print_msg = (SIMULATION_MODE) ? 'NODE SIMULATION' : 'NODE';
    // wait them all to finish
    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
        return _writeFile(parent+'/configuration_' + uid + '.json', content, 'utf8');
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + uid + ') Configuration file was saved.\n');
        return _exec('python dataset-scripts/count_main_generator.py configuration_' + uid + '.json', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + uid + ') Main generated.\n');
        var db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
        db.put(uid, JSON.stringify({'status':'running', 'step':db_msg})).catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        return _unlinkIfExists(parent + '/histogram/.main_' + uid + '.sb.src');
    }).then((msg) => {
        console.log('['+print_msg+'] Old .main_' + uid + '.sb.src deleted.\n');
        var exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh histogram/main_' : 'sharemind-scripts/sm_compile_and_run.sh histogram/main_';
        return _exec(exec_arg + uid + '.sc', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code compiled. Now running.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + uid + ') Program compiled.\n');
            return _exec('sharemind-scripts/run.sh histogram/main_' + uid + '.sb 2> out_' + uid + '.txt', {stdio:[0,1,2],cwd: parent});
        } else {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code compiled and run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE] Request(' + uid + ') Program executed.\n');
            return _exec('grep --fixed-strings --text "`grep --text "' + uid + '" /etc/sharemind/server.log | tail -n 1 | cut -d " "  -f "7-8"`" /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + uid + '.txt', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + uid + ') Program executed.\n');
        }

        if (plot) {
            return _exec('python count_plot.py ../out_' + uid + '.txt ../configuration_' + uid + '.json');
        } else {
            return _exec('python web/response.py out_' + uid + '.txt | python web/transform_response.py  configuration_' + uid + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json' , {cwd: parent});
        }
    }).then((result) => {
        if (plot) {
            console.log('['+print_msg+'] Request(' + uid + ') Plotting done.\n');
            var graph_name = result.toString();
            graph_name = graph_name.slice(0,-1);
            console.log('['+print_msg+']' + graph_name);
            res.send(graph_name);
        } else {
            console.log('['+print_msg+'] Request(' + uid + ') Response ready.\n');
            var result_obj = {'status':'succeeded','result': ''};
            result_obj.result = JSON.parse(result);
            db.put(uid, JSON.stringify(result_obj)).catch((err) => {
              console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
            });
        }
        return ;
    }).catch((err) => {
        db.put(uid, JSON.stringify({'status':'failed'}))
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
    var uid = uuidv4();
    var attributes = req.body.attributes;
    var datasources = req.body.datasources;
    var class_attribute = req.body.class_attribute;
    attributes.push(class_attribute);

    return db.put(uid, JSON.stringify({'status':'running'}));
    var plot = ('plot' in req.body); // if plot exists in req.body
    if (!plot) {
        res.status(202).json({"location" : "/smpc/queue?request="+uid});
    }
    // create array of requests for import
    var import_promises = [];
    if (SIMULATION_MODE) {
        //TODO: Generate csv from Json before importing.
        import_promises = import_locally(attributes, datasources, res, parent, uid, 'mesh');
    } else {
        import_promises = import_from_servers(attributes, datasources, res, parent, uid, '/smpc/import', 'MHMDdns.json');
    }

    var print_msg = (SIMULATION_MODE) ? 'NODE SIMULATION' : 'NODE';
    // wait them all to finish
    Promise.all(import_promises)
    .then((buffer) => {
        console.log(FgGreen + 'Importing Finished ' + ResetColor);
        return _writeFile(parent+'/configuration_' + uid + '.json', content, 'utf8');
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + uid + ') Configuration file was saved.\n');
        return _exec('python dataset-scripts/id3_main_generator.py configuration_' + uid + '.json', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('['+print_msg+'] Request(' + uid + ') Main generated.\n');
        var db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
        db.put(uid, JSON.stringify({'status':'running', 'step':db_msg})).catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        return _unlinkIfExists(parent + '/ID3/.main_' + uid + '.sb.src');
    }).then((msg) => {
        console.log('['+print_msg+'] Old .main_' + uid + '.sb.src deleted.\n');
        var exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh ID3/main_' : 'sharemind-scripts/sm_compile_and_run.sh ID3/main_';
        return _exec(exec_arg + uid + '.sc', {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code compiled. Now running.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + uid + ') Program compiled.\n');
            return _exec('sharemind-scripts/run.sh ID3/main_' + uid + '.sb  2>&1 >/dev/null | sed --expression="s/,  }/ }/g" > id3_out_' + uid + '.json', {stdio:[0,1,2],cwd: parent});
        } else {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code compiled and run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE] Request(' + uid + ') Program executed.\n');
            return _exec('grep --fixed-strings --text "`grep --text "' + uid + '" /etc/sharemind/server.log | tail -n 1 | cut -d " "  -f "7-8"`" /etc/sharemind/server.log | cut -d " "  -f "9-" | sed --expression="s/,  }/ }/g" >  out_' + uid + '.json', {stdio:[0,1,2],cwd: parent});
        }
    }).then((buffer) => {
        if (SIMULATION_MODE) {
            db.put(uid, JSON.stringify({'status':'running', 'step':'SecreC code run. Now generating output.'})).catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
            console.log('[NODE SIMULATION] Request(' + uid + ') Program executed.\n');
        }

        if (plot) {
            return _exec('python web/id3_response.py out_' + uid + '.json configuration_' + uid + '.json --plot --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {cwd: parent});
        } else {
            return _exec('python web/id3_response.py out_' + uid + '.json configuration_' + uid + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {cwd: parent});
        }
    }).then((result) => {
        if (plot) {
            console.log('['+print_msg+'] Request(' + uid + ') Plotting done.\n');
            var graph_name = result.toString();
            graph_name = graph_name.slice(0,-1);
            console.log('['+print_msg+']' + graph_name);
            res.send(graph_name);
        } else {
            console.log('['+print_msg+'] Request(' + uid + ') Response ready.\n');
            var result_obj = {'status':'succeeded','result': ''};
            result_obj.result = JSON.parse(result);
            db.put(uid, JSON.stringify(result_obj)).catch((err) => {
              console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
            });
        }
        return ;
    }).catch((err) => {
        db.put(uid, JSON.stringify({'status':'failed'}))
        .catch((err) => {
            console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
        });
        console.log(FgRed + '['+print_msg+'] ' + ResetColor + err);
    });
});



const port = 3000;
app.listen(port, () => console.log('Example app listening on port ' + port + '!'));

const FgRed = "\x1b[31m";
const FgGreen = "\x1b[32m";
const ResetColor = "\x1b[0m";
