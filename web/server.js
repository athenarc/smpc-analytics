let SIMULATION_MODE = false;
process.argv.forEach(function (val) {
    if (val === '-sim' || val === '--sim' || val === '-simulation' || val === '--simulation') {
        SIMULATION_MODE = true;
    }
});
const print_msg = (SIMULATION_MODE) ? 'NODE SIMULATION' : 'NODE';


if (SIMULATION_MODE) {
    console.log('\n[NODE SIMULATION] Running in simulation mode\n');
} else {
    console.log('\n[NODE] Running in Secure Multiparty Computation mode with 3 servers\n');
}

// Imports
const https = require('https');
const http = require('http');
const express = require('express');
const {exec} = require('child_process');
const {execSync} = require('child_process');
const fs = require('fs');
const uuidv4 = require('uuid/v4');
const path = require('path');
const bodyParser = require('body-parser');
const morgan = require('morgan'); // for requests logging
const morganBody = require('morgan-body');
const level = require('level'); // leveldb for requests-status and cache
const rp = require('request-promise');
const DateDiff = require('date-diff');

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

const frontend = __dirname + "/frontend/";
global.__basedir = __dirname;
const log_stream = fs.createWriteStream(path.join(__dirname, 'requests.log'), {flags: 'a'});
morganBody(app, {stream: log_stream}); // log request body

app.use(morgan(':remote-addr \\n\\n', {stream: log_stream})); // log request IP
const db = level('./mydb');
const cachedb = level('./cache-database');


app.get('/', function (req, res) {
    res.sendFile(path.join(frontend + 'index.html'));
});

app.use(express.static(path.join(__dirname, 'frontend'))); // public/static files
app.use("/visuals", express.static(__dirname + '/visuals'));
app.use("/graphs", express.static(__dirname + '/graphs'));


if (fs.existsSync('./sslcert/fullchain.pem')) {
    const options = {
        cert: fs.readFileSync('./sslcert/fullchain.pem'),
        key: fs.readFileSync('./sslcert/privkey.pem')
    };

    const http_port = 80;
    const https_port = 443;
    http.createServer(function (req, res) {
        if ('headers' in req && 'host' in req.headers) {
            res.writeHead(307, {"Location": "https://" + req.headers.host.replace(http_port, https_port) + req.url});
            console.log("http request, will go to >> ");
            console.log("https://" + req.headers.host.replace(http_port, https_port) + req.url);
            res.end();
        }
    }).listen(http_port);

    // app.listen(port, () => console.log('Example app listening on port ' + port + '!'));
    https.createServer(options, app).listen(https_port, () => console.log('Example app listening on port ' + http_port + '!'));
} else {
    const port = 3000;
    app.listen(port, () => console.log('Example app listening on port ' + port + '!'));
}


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
        fs.stat(filename, (err) => {
            if (err === null) {
                fs.unlink(filename, err => {
                    if (err) {
                        return reject(err);
                    }
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
    const uri = mhmdDNS[datasrc];
    const options = {                       // Configure the request
        method: 'POST',
        uri: 'http://' + uri + action,
        body: {
            "attributes": attributes,
            "datasource": datasrc + '_' + uid
        },
        json: true                        // Automatically stringifies the body to JSON
    };

    console.log(FgGreen + 'Request for import sent to: ' + datasrc + ' at ' + uri + ResetColor);
    return rp(options);                   // Return promise to start the request
}

// function to send requests for import and return array of promises
function import_from_servers(attributes, datasources, res, parent, uid, action, DNSfile) {
    const mhmdDNS = JSON.parse(fs.readFileSync(DNSfile, 'utf8'));
    if (typeof datasources === 'undefined') {
        datasources = Object.keys(mhmdDNS);
    }
    for (let datasrc of datasources) {        // Check that all IPs exist
        if ((datasrc in mhmdDNS) === false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find IP for ' + datasrc + ', it does not exist in MHMDdns.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }
    // since no error occured in the above loop, we have all IPs
    db.put(uid, JSON.stringify({'status': 'running', 'step': 'Securely importing data'}));

    // // send the requests for import
    const import_promises = [];
    for (let datasrc of datasources) {
        import_promises.push(_sendRequest(datasrc, mhmdDNS, attributes, uid, action));
    }
    // return array of promises for import
    return import_promises;
}


// function to import local data and return promise
function import_locally(attributes, datasources, res, parent, uid, type) {
    const localDNS = JSON.parse(fs.readFileSync('localDNS.json', 'utf8'));
    if (typeof datasources === 'undefined') {
        datasources = Object.keys(localDNS);
    }
    for (let datasrc of datasources) {         // Check that all IPs exist
        if ((datasrc in localDNS) === false) {  // If datasrc does not exist in DNS file, continue
            console.log(FgRed + 'Error: ' + ResetColor + 'Unable to find path for ' + datasrc + ', it does not exist in localDNS.json file.');
            return res.status(400).send('Failure on data importing from ' + datasrc);
        }
    }

    if (type === 'mesh') {
        // var json_to_csv_promises = [];
        for (let datasrc of datasources) {
            const patient_file = localDNS[datasrc][type];
            const csv_file = './datasets/' + datasrc + '_' + uid + '.csv';
            localDNS[datasrc][type] = csv_file;
            console.log('[NODE SIMULATION] python mhmd-driver/mesh_json_to_csv.py \"' + attributes.join(' ') + '\" ' + patient_file + ' --output ' + csv_file + ' --mtrees ./mhmd-driver/m.json --mtrees_inverted ./mhmd-driver/m_inv.json --mapping ./mhmd-driver/mesh_mapping.json\n');
            execSync('python mhmd-driver/mesh_json_to_csv.py \"' + attributes.join(' ') + '\" ' + patient_file + ' --output ' + csv_file + ' --mtrees ./mhmd-driver/m.json --mtrees_inverted ./mhmd-driver/m_inv.json --mapping ./mhmd-driver/mesh_mapping.json', {
                stdio: [0, 1, 2],
                cwd: parent,
                shell: '/bin/bash'
            });
        }
    }

    const import_promises = [];
    // exec asynch python simulated imports
    for (let datasrc of datasources) {
        const dataset = localDNS[datasrc][type];
        console.log('[NODE SIMULATION] Request(' + uid + ') python ./dataset-scripts/simulated_import.py ' + dataset + ' --attributes "' + attributes.join(';') + '" --table "' + datasrc + '_' + uid + '"\n');
        import_promises.push(_exec('python ./dataset-scripts/simulated_import.py ' + dataset + ' --attributes "' + attributes.join(';') + '" --table "' + datasrc + '_' + uid + '"', {
            stdio: [0, 1, 2],
            cwd: parent,
            shell: '/bin/bash'
        }));
    }
    // return array of promises for import
    return import_promises;
}


app.options('/*', function (req, res) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    res.sendStatus(200);
});

app.get('/smpc/queue', function (req, res) {
    let request = req.query.request;
    db.get(request)
    .then((value) => {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.status(200).json(JSON.parse(value));
    }).catch((err) => {
        console.log(FgRed + '[NODE] ' + ResetColor + err);
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.status(200).json({'status': 'notstarted'});
    });
});


app.post('/smpc/histogram', function (req, res) {
    let i;
    const parent = path.dirname(__basedir);
    const content = JSON.stringify(req.body);
    console.log(content);
    const uid = uuidv4();
    const attributes = req.body.attributes;
    const datasources = req.body.datasources;
    const use_cache = req.body.cache;

    db.put(uid, JSON.stringify({'status': 'running'}));
    let plot = ('plot' in req.body); // if plot exists in req.body
    if (!plot) {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.status(202).json({"location": "/smpc/queue?request=" + uid});
    }
    // create list of attribute names from the POST request
    let attrib;
    const attributes_to_import = [];
    for (i = 0; i < attributes.length; i++) {
        for (let j = 0; j < attributes[i].length; j++) {
            attrib = attributes[i][j].name;
            if (attributes_to_import.indexOf(attrib) === -1) { // if attribute does not exist in list (avoid duplicate imports)
                attributes_to_import.push(attrib);
            }
        }
    }

    let request_key;
    // if filters are defined
    if ('filters' in req.body) {
        const filters = req.body.filters;
        // Add filter attributes for importing to list
        for (i = 0; i < filters.conditions.length; i++) {
            attrib = filters.conditions[i].attribute;
            if (attributes_to_import.indexOf(attrib) === -1) { // if attribute does not exist in list (avoid duplicate imports)
                attributes_to_import.push(attrib);
            }
        }
        request_key = JSON.stringify({'attributes': attributes[0], 'datasources': datasources, 'filters': filters, 'plot': plot});
    } else {
        request_key = JSON.stringify({'attributes': attributes[0], 'datasources': datasources, 'plot': plot});
    }

    // Check if request has been already computed
    let not_use_cache = false;
    if ('cache' in req.body) {
        not_use_cache = use_cache.toUpperCase() === "NO";
    }
    cachedb.get(request_key)
    .then((value) => {
        if (not_use_cache) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') User has set the flag cache to NO in request body, goind to recompute it!\n' + ResetColor);
            throw "User has set the flag cache to NO in request body, goind to recompute it!"; // go to catch
        }
        console.log('[' + print_msg + '] ' + FgGreen + 'Request(' + uid + ') Key: ' + request_key + ' found in cache-db!\n' + ResetColor);

        let value_array = value.split(", date:");
        let diff = new DateDiff(new Date(), new Date(value_array[1]));
        // if previous computation was a month ago, recompute it
        if (diff.days() > 30) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' has expired, goind to recompute it!\n' + ResetColor);
            cachedb.del(request_key).catch((err) => { // delete previous result
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            throw "Result has expired, goind to recompute it!"; // go to catch
        }

        let result = value_array[0];
        if (plot) {
            res.send(result.slice(1, -1)); // slice is for removing quotes from string.
        } else {
            console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
            const result_obj = {'status': 'succeeded', 'result': ''};
            result_obj.result = JSON.parse(result);
            db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
        }
    }).catch(() => { // If request has not been computed
        console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' not found in cache-db.\n' + ResetColor);

        let import_promises = [];
        if (SIMULATION_MODE) {
            import_promises = import_locally(attributes_to_import, datasources, res, parent, uid, 'cvi');
        } else {
            import_promises = import_from_servers(attributes_to_import, datasources, res, parent, uid, '/smpc/import/cvi', 'MHMDdns_cvi.json');
        }

        Promise.all(import_promises)
        .then(() => {
                console.log(FgGreen + 'Importing Finished ' + ResetColor);
                return _writeFile(parent + '/configuration_' + uid + '.json', content, 'utf8');
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Configuration file was saved.\n');
            if (SIMULATION_MODE) {
                return _exec('python dataset-scripts/main_generator.py configuration_' + uid + '.json --DNS web/localDNS.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            } else {
                return _exec('python dataset-scripts/main_generator.py configuration_' + uid + '.json --DNS web/MHMDdns_cvi.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            }
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Main generated.\n');
            const db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
            db.put(uid, JSON.stringify({'status': 'running', 'step': db_msg})).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            return _unlinkIfExists(parent + '/histogram/.main_' + uid + '.sb.src');
        }).then(() => {
            console.log('[' + print_msg + '] Old .main_' + uid + '.sb.src deleted.\n');
            const exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh histogram/main_' : 'sharemind-scripts/sm_compile_and_run.sh histogram/main_';
            return _exec(exec_arg + uid + '.sc', {stdio: [0, 1, 2], cwd: parent, shell: '/bin/bash'});
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled. Now running.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program compiled.\n');
                return _exec('sharemind-scripts/run.sh histogram/main_' + uid + '.sb 2> out_' + uid + '.txt', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            } else {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled and run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE] Request(' + uid + ') Program executed.\n');
                return _exec('grep --fixed-strings --text "`grep --text "' + uid + '" /etc/sharemind/server.log | tail -n 1 | cut -d " "  -f "7-8"`" /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + uid + '.txt', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            }
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program executed.\n');
            }

            if (plot) {
                return _exec('python plot.py ../configuration_' + uid + '.json');
            } else {
                return _exec('python web/response.py out_' + uid + '.txt', {cwd: parent, shell: '/bin/bash'});
            }
        }).then((result) => {
            let request_cache_result;
            if (plot) {
                console.log('[' + print_msg + '] Request(' + uid + ') Plotting done.\n');
                let graph_name = result.toString();
                graph_name = graph_name.slice(0, -1);
                console.log('[' + print_msg + '] Request(' + uid + ') ' + graph_name);
                res.send(graph_name);
                request_cache_result = JSON.stringify(result.replace(/\n/g, ''));
            } else {
                console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
                const result_obj = {'status': 'succeeded', 'result': ''};
                result_obj.result = JSON.parse(result);
                db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                    console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
                });
                request_cache_result = result;
            }

            cachedb.put(request_key, request_cache_result + ", date:" + new Date())
            .catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
        }).catch((err) => {
            db.put(uid, JSON.stringify({'status': 'failed'}))
            .catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            res.sendStatus(400);
        });
    });
});


app.post('/smpc/count', function (req, res) {
    const parent = path.dirname(__basedir);
    const content = JSON.stringify(req.body);
    console.log(content);
    const uid = uuidv4();
    const attributes = req.body.attributes;
    const datasources = req.body.datasources;
    const use_cache = req.body.cache;
    let attrib;

    let plot = ('plot' in req.body); // if plot exists in req.body
    db.put(uid, JSON.stringify({'status': 'running'}));
    if (!plot) {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.status(202).json({"location": "/smpc/queue?request=" + uid});
    }

    // if filters are defined
    let request_key;
    if ('filters' in req.body) {
        const filters = req.body.filters;
        // Add filter attributes for importing to list
        for (let i = 0; i < filters.conditions.length; i++) {
            attrib = filters.conditions[i].attribute;
            if (attributes.indexOf(attrib) === -1) { // if attribute does not exist in list (avoid duplicate imports)
                attributes.push(attrib);
            }
        }
        request_key = JSON.stringify({'attributes': attributes, 'datasources': datasources, 'filters': filters, 'plot': plot});
    } else {
        request_key = JSON.stringify({'attributes': attributes, 'datasources': datasources, 'plot': plot});
    }

    // Check if request has been already computed
    let not_use_cache = false;
    if ('cache' in req.body) {
        not_use_cache = use_cache.toUpperCase() === "NO";
    }
    cachedb.get(request_key)
    .then((value) => {
        if (not_use_cache) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') User has set the flag cache to NO in request body, goind to recompute it!\n' + ResetColor);
            throw "User has set the flag cache to NO in request body, goind to recompute it!"; // go to catch
        }
        console.log('[' + print_msg + '] ' + FgGreen + 'Request(' + uid + ') Key: ' + request_key + ' found in cache-db!\n' + ResetColor);

        let value_array = value.split(", date:");
        let diff = new DateDiff(new Date(), new Date(value_array[1]));
        // if previous computation was a month ago, recompute it
        if (diff.days() > 30) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' has expired, goind to recompute it!\n' + ResetColor);
            cachedb.del(request_key).catch((err) => { // delete previous result
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            throw "Result has expired, goind to recompute it!"; // go to catch
        }

        let result = value_array[0];
        if (plot) {
            res.send(result.slice(1, -1)); // slice is for removing quotes from string.
        } else {
            console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
            const result_obj = {'status': 'succeeded', 'result': ''};
            result_obj.result = JSON.parse(result);
            db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
        }
    }).catch(() => { // If request has not been computed
        console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' not found in cache-db.\n' + ResetColor);

        // create array of requests for import
        let import_promises = [];
        if (SIMULATION_MODE) {
            import_promises = import_locally(attributes, datasources, res, parent, uid, 'mesh');
        } else {
            import_promises = import_from_servers(attributes, datasources, res, parent, uid, '/smpc/import', 'MHMDdns.json');
        }

        // wait them all to finish
        Promise.all(import_promises)
        .then(() => {
            console.log(FgGreen + 'Importing Finished ' + ResetColor);
            return _writeFile(parent + '/configuration_' + uid + '.json', content, 'utf8');
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Configuration file was saved.\n');
            if (SIMULATION_MODE) {
                return _exec('python dataset-scripts/count_main_generator.py configuration_' + uid + '.json --DNS web/localDNS.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            } else {
                return _exec('python dataset-scripts/count_main_generator.py configuration_' + uid + '.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            }
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Main generated.\n');
            const db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
            db.put(uid, JSON.stringify({'status': 'running', 'step': db_msg})).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            return _unlinkIfExists(parent + '/histogram/.main_' + uid + '.sb.src');
        }).then(() => {
            console.log('[' + print_msg + '] Old .main_' + uid + '.sb.src deleted.\n');
            const exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh histogram/main_' : 'sharemind-scripts/sm_compile_and_run.sh histogram/main_';
            return _exec(exec_arg + uid + '.sc', {stdio: [0, 1, 2], cwd: parent, shell: '/bin/bash'});
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled. Now running.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program compiled.\n');
                return _exec('sharemind-scripts/run.sh histogram/main_' + uid + '.sb 2> out_' + uid + '.txt', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            } else {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled and run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE] Request(' + uid + ') Program executed.\n');
                return _exec('grep --fixed-strings --text "`grep --text "' + uid + '" /etc/sharemind/server.log | tail -n 1 | cut -d " "  -f "7-8"`" /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + uid + '.txt', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            }
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program executed.\n');
            }

            if (plot) {
                return _exec('python count_plot.py ../out_' + uid + '.txt ../configuration_' + uid + '.json');
            } else {
                return _exec('python web/response.py out_' + uid + '.txt | python web/transform_response.py  configuration_' + uid + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {
                    cwd: parent,
                    shell: '/bin/bash'
                });
            }
        }).then((result) => {
            let request_cache_result;
            if (plot) {
                console.log('[' + print_msg + '] Request(' + uid + ') Plotting done.\n');
                let graph_name = result.toString();
                graph_name = graph_name.slice(0, -1);
                console.log('[' + print_msg + '] Request(' + uid + ') ' + graph_name);
                res.send(graph_name);
                request_cache_result = JSON.stringify(result.replace(/\n/g, ''));
            } else {
                console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
                const result_obj = {'status': 'succeeded', 'result': ''};
                result_obj.result = JSON.parse(result);
                db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                    console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
                });
                request_cache_result = result;
            }

            cachedb.put(request_key, request_cache_result + ", date:" + new Date())
            .catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
        }).catch((err) => {
            db.put(uid, JSON.stringify({'status': 'failed'}))
            .catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            res.sendStatus(400);
        });
    });
});


app.post('/smpc/decision_tree/numerical', function (req, res) {
    const parent = path.dirname(__basedir);
    const content = JSON.stringify(req.body);
    console.log(content);
    const uid = uuidv4();
    const attributes = req.body.attributes;
    const datasources = req.body.datasources;
    const class_attribute = req.body.class_attribute.name;
    const classifier = ('classifier' in req.body) ? req.body.classifier : "ID3";
    const use_cache = req.body.cache;

    db.put(uid, JSON.stringify({'status': 'running'}));
    let plot = ('plot' in req.body); // if plot exists in req.body
    if (!plot) {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.status(202).json({"location": "/smpc/queue?request=" + uid});
    }

    // create list of attribute names from the POST request
    let attrib;
    const attributes_to_import = [];
    for (let i = 0; i < attributes.length; i++) {
        attrib = attributes[i].name;
        if (attributes_to_import.indexOf(attrib) === -1) { // if attribute does not exist in list (avoid duplicate imports)
            attributes_to_import.push(attrib);
        }
    }
    attributes_to_import.push(class_attribute);

    // Check if request has been already computed
    let not_use_cache = false;
    if ('cache' in req.body) {
        not_use_cache = use_cache.toUpperCase() === "NO";
    }
    let request_key = JSON.stringify({'attributes': attributes, 'class_attribute': class_attribute, 'classifier': classifier, 'datasources': datasources, 'plot': plot});
    cachedb.get(request_key)
    .then((value) => {
        if (not_use_cache) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') User has set the flag cache to NO in request body, goind to recompute it!\n' + ResetColor);
            throw "User has set the flag cache to NO in request body, goind to recompute it!"; // go to catch
        }
        console.log('[' + print_msg + '] ' + FgGreen + 'Request(' + uid + ') Key: ' + request_key + ' found in cache-db!\n' + ResetColor);

        let value_array = value.split(", date:");
        let diff = new DateDiff(new Date(), new Date(value_array[1]));
        // if previous computation was a month ago, recompute it
        if (diff.days() > 30) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' has expired, goind to recompute it!\n' + ResetColor);
            cachedb.del(request_key).catch((err) => { // delete previous result
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            throw "Result has expired, goind to recompute it!"; // go to catch
        }

        let result = value_array[0];
        if (plot) {
            res.send(result.slice(1, -1)); // slice is for removing quotes from string.
        } else {
            console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
            const result_obj = {'status': 'succeeded', 'result': ''};
            result_obj.result = JSON.parse(result);
            db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
        }
    }).catch(() => { // If request has not been computed
        console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' not found in cache-db.\n' + ResetColor);

        // create array of requests for import
        let import_promises = [];
        if (SIMULATION_MODE) {
            import_promises = import_locally(attributes_to_import, datasources, res, parent, uid, 'cvi');
        } else {
            import_promises = import_from_servers(attributes_to_import, datasources, res, parent, uid, '/smpc/import/cvi', 'MHMDdns.json');
        }

        // wait them all to finish
        Promise.all(import_promises)
        .then(() => {
            console.log(FgGreen + 'Importing Finished ' + ResetColor);
            return _writeFile(parent + '/configuration_' + uid + '.json', content, 'utf8');
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Configuration file was saved.\n');
            if (SIMULATION_MODE) {
                if (classifier === "ID3") {
                    return _exec('python dataset-scripts/id3_numerical_main_generator.py configuration_' + uid + '.json --DNS web/localDNS.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python dataset-scripts/c45_main_generator.py configuration_' + uid + '.json --DNS web/localDNS.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            } else {
                if (classifier === "ID3") {
                    return _exec('python dataset-scripts/id3_numerical_main_generator.py configuration_' + uid + '.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python dataset-scripts/c45_main_generator.py configuration_' + uid + '.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            }
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Main generated.\n');
            const db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
            db.put(uid, JSON.stringify({'status': 'running', 'step': db_msg})).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            return _unlinkIfExists(parent + '/decision-tree/.main_' + uid + '.sb.src');
        }).then(() => {
            console.log('[' + print_msg + '] Old .main_' + uid + '.sb.src deleted.\n');
            const exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh decision-tree/main_' : 'sharemind-scripts/sm_compile_and_run.sh decision-tree/main_';
            return _exec(exec_arg + uid + '.sc', {stdio: [0, 1, 2], cwd: parent, shell: '/bin/bash'});
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled. Now running.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program compiled.\n');
                return _exec('set -o pipefail && sharemind-scripts/run.sh decision-tree/main_' + uid + '.sb  2>&1 >/dev/null | sed --expression="s/,  }/ }/g" > out_' + uid + '.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            } else {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled and run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE] Request(' + uid + ') Program executed.\n');
                return _exec('grep --fixed-strings --text "`grep --text "' + uid + '" /etc/sharemind/server.log | tail -n 1 | cut -d " "  -f "7-8"`" /etc/sharemind/server.log | cut -d " "  -f "9-" | sed --expression="s/,  }/ }/g" >  out_' + uid + '.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            }
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program executed.\n');
            }

            if (plot) {
                if (classifier === "ID3") {
                    return _exec('python web/id3_numerical_response.py out_' + uid + '.json configuration_' + uid + '.json --plot', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python web/c45_response.py out_' + uid + '.json configuration_' + uid + '.json --plot', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            } else {
                if (classifier === "ID3") {
                    return _exec('python web/id3_numerical_response.py out_' + uid + '.json configuration_' + uid + '.json', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python web/c45_response.py out_' + uid + '.json configuration_' + uid + '.json', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            }
        }).then((result) => {
            let request_cache_result;
            if (plot) {
                console.log('[' + print_msg + '] Request(' + uid + ') Plotting done.\n');
                let graph_name = result.toString();
                graph_name = graph_name.slice(0, -1);
                console.log('[' + print_msg + '] Request(' + uid + ') ' + graph_name);
                res.send(graph_name);
                request_cache_result = JSON.stringify(result.replace(/\n/g, ''));
            } else {
                console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
                const result_obj = {'status': 'succeeded', 'result': ''};
                result_obj.result = JSON.parse(result);
                db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                    console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
                });
                request_cache_result = result;
            }

            cachedb.put(request_key, request_cache_result + ", date:" + new Date())
            .catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
        }).catch((err) => {
            db.put(uid, JSON.stringify({'status': 'failed'}))
            .catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            res.sendStatus(400);
        });
    });
});


app.post('/smpc/decision_tree/categorical', function (req, res) {
    const parent = path.dirname(__basedir);
    const content = JSON.stringify(req.body);
    console.log(content);
    const uid = uuidv4();
    const attributes = req.body.attributes;
    const datasources = req.body.datasources;
    const class_attribute = req.body.class_attribute;
    const classifier = ('classifier' in req.body) ? req.body.classifier : "ID3";
    const use_cache = req.body.cache;

    db.put(uid, JSON.stringify({'status': 'running'}));
    let plot = ('plot' in req.body); // if plot exists in req.body
    if (!plot) {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.status(202).json({"location": "/smpc/queue?request=" + uid});
    }

    // Check if request has been already computed
    let not_use_cache = false;
    if ('cache' in req.body) {
        not_use_cache = use_cache.toUpperCase() === "NO";
    }
    let request_key = JSON.stringify({'attributes': attributes, 'class_attribute': class_attribute, 'classifier': classifier, 'datasources': datasources, 'plot': plot});
    attributes.push(class_attribute);
    cachedb.get(request_key)
    .then((value) => {
        if (not_use_cache) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') User has set the flag cache to NO in request body, goind to recompute it!\n' + ResetColor);
            throw "User has set the flag cache to NO in request body, goind to recompute it!"; // go to catch
        }
        console.log('[' + print_msg + '] ' + FgGreen + 'Request(' + uid + ') Key: ' + request_key + ' found in cache-db!\n' + ResetColor);
        let value_array = value.split(", date:");
        let diff = new DateDiff(new Date(), new Date(value_array[1]));
        // if previous computation was a month ago, recompute it
        if (diff.days() > 30) {
            console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' has expired, goind to recompute it!\n' + ResetColor);
            cachedb.del(request_key).catch((err) => { // delete previous result
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            throw "Result has expired, goind to recompute it!"; // go to catch
        }

        let result = value_array[0];
        if (plot) {
            res.send(result.slice(1, -1)); // slice is for removing quotes from string.
        } else {
            console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
            const result_obj = {'status': 'succeeded', 'result': ''};
            result_obj.result = JSON.parse(result);
            db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
        }
    }).catch(() => { // If request has not been computed
        console.log('[' + print_msg + '] ' + FgYellow + 'Request(' + uid + ') Key: ' + request_key + ' not found in cache-db.\n' + ResetColor);

        // create array of requests for import
        let import_promises = [];
        if (SIMULATION_MODE) {
            import_promises = import_locally(attributes, datasources, res, parent, uid, 'mesh');
        } else {
            import_promises = import_from_servers(attributes, datasources, res, parent, uid, '/smpc/import', 'MHMDdns.json');
        }

        // wait them all to finish
        Promise.all(import_promises)
        .then(() => {
            console.log(FgGreen + 'Importing Finished ' + ResetColor);
            return _writeFile(parent + '/configuration_' + uid + '.json', content, 'utf8');
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Configuration file was saved.\n');
            if (SIMULATION_MODE) {
                if (classifier === "ID3") {
                    return _exec('python dataset-scripts/id3_main_generator.py configuration_' + uid + '.json --DNS web/localDNS.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python dataset-scripts/c45_main_generator.py configuration_' + uid + '.json --DNS web/localDNS.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            } else {
                if (classifier === "ID3") {
                    return _exec('python dataset-scripts/id3_main_generator.py configuration_' + uid + '.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python dataset-scripts/c45_main_generator.py configuration_' + uid + '.json', {
                        stdio: [0, 1, 2],
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            }
        }).then(() => {
            console.log('[' + print_msg + '] Request(' + uid + ') Main generated.\n');
            const db_msg = (SIMULATION_MODE) ? 'SecreC code generated. Now compiling.' : 'SecreC code generated. Now compiling and running.';
            db.put(uid, JSON.stringify({'status': 'running', 'step': db_msg})).catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            return _unlinkIfExists(parent + '/decision-tree/.main_' + uid + '.sb.src');
        }).then(() => {
            console.log('[' + print_msg + '] Old .main_' + uid + '.sb.src deleted.\n');
            const exec_arg = (SIMULATION_MODE) ? 'sharemind-scripts/compile.sh decision-tree/main_' : 'sharemind-scripts/sm_compile_and_run.sh decision-tree/main_';
            return _exec(exec_arg + uid + '.sc', {stdio: [0, 1, 2], cwd: parent, shell: '/bin/bash'});
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled. Now running.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program compiled.\n');
                return _exec('set -o pipefail && sharemind-scripts/run.sh decision-tree/main_' + uid + '.sb  2>&1 >/dev/null | sed --expression="s/,  }/ }/g" > out_' + uid + '.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            } else {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code compiled and run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE] Request(' + uid + ') Program executed.\n');
                return _exec('grep --fixed-strings --text "`grep --text "' + uid + '" /etc/sharemind/server.log | tail -n 1 | cut -d " "  -f "7-8"`" /etc/sharemind/server.log | cut -d " "  -f "9-" | sed --expression="s/,  }/ }/g" >  out_' + uid + '.json', {
                    stdio: [0, 1, 2],
                    cwd: parent,
                    shell: '/bin/bash'
                });
            }
        }).then(() => {
            if (SIMULATION_MODE) {
                db.put(uid, JSON.stringify({
                    'status': 'running',
                    'step': 'SecreC code run. Now generating output.'
                })).catch((err) => {
                    console.log(FgRed + '[NODE] ' + ResetColor + err);
                });
                console.log('[NODE SIMULATION] Request(' + uid + ') Program executed.\n');
            }

            if (plot) {
                if (classifier === "ID3") {
                    return _exec('python web/id3_response.py out_' + uid + '.json configuration_' + uid + '.json --plot --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python web/c45_response.py out_' + uid + '.json configuration_' + uid + '.json --plot --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            } else {
                if (classifier === "ID3") {
                    return _exec('python web/id3_response.py out_' + uid + '.json configuration_' + uid + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                } else if (classifier === "C45") {
                    return _exec('python web/c45_response.py out_' + uid + '.json configuration_' + uid + '.json --mapping mhmd-driver/mesh_mapping.json --mtrees_inverted mhmd-driver/m_inv.json', {
                        cwd: parent,
                        shell: '/bin/bash'
                    });
                }
            }
        }).then((result) => {
            let request_cache_result;
            if (plot) {
                console.log('[' + print_msg + '] Request(' + uid + ') Plotting done.\n');
                let graph_name = result.toString();
                graph_name = graph_name.slice(0, -1);
                console.log('[' + print_msg + '] Request(' + uid + ') ' + graph_name);
                res.send(graph_name);
                request_cache_result = JSON.stringify(result.replace(/\n/g, ''));
            } else {
                console.log('[' + print_msg + '] Request(' + uid + ') Response ready.\n');
                const result_obj = {'status': 'succeeded', 'result': ''};
                result_obj.result = JSON.parse(result);
                db.put(uid, JSON.stringify(result_obj)).catch((err) => {
                    console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
                });
                request_cache_result = result;
            }

            cachedb.put(request_key, request_cache_result + ", date:" + new Date())
            .catch((err) => {
                console.log(FgRed + '[NODE] ' + ResetColor + err);
            });
        }).catch((err) => {
            db.put(uid, JSON.stringify({'status': 'failed'}))
            .catch((err) => {
                console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            });
            console.log(FgRed + '[' + print_msg + '] ' + ResetColor + err);
            res.sendStatus(400);
        });
    });
});


const FgRed = "\x1b[31m";
const FgGreen = "\x1b[32m";
const FgYellow = "\x1b[33m";
const ResetColor = "\x1b[0m";
