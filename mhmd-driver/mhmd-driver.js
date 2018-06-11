console.log('\n[NODE] Running within Docker\n');
const express = require('express');
const app = express();
const { exec } = require('child_process');
const fs = require('fs');
var path = require('path');
var bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
global.__basedir = __dirname;


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


app.post('/smpc/import', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);

    var attributes = req.body.attributes;
    var hospitalName = req.body.datasource;
    console.log('[NODE] Going to import dataset from /patients.json, /mesh_mapping.json, /m.json, /m_inv.json, for attributes ' + attributes + '\n');
    console.log('[NODE] Running CSV-preprocessor.');
    console.log('\tpython /mhmd-driver/mesh_json_to_csv.py \"' + attributes.join(' ')  + '\" /patients.json --output /' + hospitalName + '.csv\n');
    _exec('python /mhmd-driver/mesh_json_to_csv.py \"' + attributes.join(' ') + '\" /patients.json --output /' + hospitalName + '.csv', {stdio:[0,1,2],cwd: parent})
    .then((buffer) => {
        console.log('[NODE] Running XML-Generator');
        console.log('\tpython /mhmd-driver/xml_generator.py /' + hospitalName + '.csv --float --table ' + hospitalName + '\n');
        return _exec('python /mhmd-driver/xml_generator.py /' + hospitalName + '.csv --float --table ' + hospitalName, {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('[NODE] Running CSV-Importer');
        console.log('\tsharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /' + hospitalName + '.csv --model /' + hospitalName + '.xml --separator c --log /' + hospitalName + '.log\n');
        return _exec('sharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /' + hospitalName + '.csv --model /' + hospitalName + '.xml --separator c --log /' + hospitalName + '.log', {stdio:[0,1,2],cwd: parent});
    }).then((result) => {
        console.log('[NODE] Now unlinking intermidiate files.\n');
        // remove intermidiate files
        var unlink_promises = [];
        unlink_promises.push( _unlinkIfExists(parent + '/' + hospitalName + '.csv') );
        unlink_promises.push( _unlinkIfExists(parent + '/' + hospitalName + '.xml') );
        unlink_promises.push( _unlinkIfExists(parent + '/' + hospitalName + '.log') );

        return Promise.all(unlink_promises);
    }).then((result) => {
        console.log('[NODE] Data importing Successful.\n');
        res.end();
    }).catch((err) => {
        console.log('[NODE] Failure on data importing.\n');
        console.log(err);
        res.status(400).send('Failure on data importing');
    });
});


app.post('/smpc/import/cvi', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);

    var attributes = req.body.attributes;
    var hospitalName = req.body.datasource;
    console.log('[NODE] Going to import CVI dataset, for attributes ' + attributes + '\n');
    console.log('[NODE] Running CSV-filter.');
    console.log('\tpython /mhmd-driver/csv_filter.py \"' + attributes.join(';')  + '\" --path /cvi_identified.csv --output /cvi_identified_' + hospitalName + '_filtered.csv\n');
    _exec('\tpython /mhmd-driver/csv_filter.py \"' + attributes.join(';')  + '\" --path /cvi_identified.csv --output /cvi_identified_' + hospitalName + '_filtered.csv', {stdio:[0,1,2],cwd: parent})
    .then((buffer) => {
        console.log('[NODE] Running XML-Generator');
        console.log('\tpython /mhmd-driver/xml_generator.py /cvi_identified_' + hospitalName + '_filtered.csv --table ' + hospitalName + '\n');
        return _exec('python /mhmd-driver/xml_generator.py /cvi_identified_' + hospitalName + '_filtered.csv --table ' + hospitalName, {stdio:[0,1,2],cwd: parent});
    }).then((buffer) => {
        console.log('[NODE] Running CSV-Importer');
        console.log('\tsharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /cvi_identified_' + hospitalName + '_filtered.csv --model /cvi_identified_' + hospitalName + '_filtered.xml --separator c --log /cvi_identified_' + hospitalName + '_filtered.log\n');
        return _exec('sharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /cvi_identified_' + hospitalName + '_filtered.csv --model /cvi_identified_' + hospitalName + '_filtered.xml --separator c --log /cvi_identified_' + hospitalName + '_filtered.log', {stdio:[0,1,2],cwd: parent});
    }).then((result) => {
        console.log('[NODE] Now unlinking intermidiate files.\n');
        // remove intermidiate files
        var unlink_promises = [];
        unlink_promises.push( _unlinkIfExists(parent + '/cvi_identified_' + hospitalName + '_filtered.csv') );
        unlink_promises.push( _unlinkIfExists(parent + '/cvi_identified_' + hospitalName + '_filtered.xml') );
        unlink_promises.push( _unlinkIfExists(parent + '/cvi_identified_' + hospitalName + '_filtered.log') );

        return Promise.all(unlink_promises);
    }).then((result) => {
        console.log('[NODE] Data importing Successful.\n');
        res.end();
    }).catch((err) => {
        console.log('[NODE] Failure on data importing.\n');
        console.log(err);
        res.status(400).send('Failure on data importing');
    });
});


// // With CSV preprocessor, for categorical values needs enhancments
// app.post('/smpc/import/cvi', function(req, res) {
//     var parent = path.dirname(__basedir);
//     var content = JSON.stringify(req.body);
//     var attributes = req.body.attributes;
//     var hospitalName = req.body.datasource;
//     console.log('[NODE] Going to import CVI dataset, for attributes ' + attributes + '\n');
//     console.log('[NODE] Running CSV-filter.');
//     console.log('\tpython /mhmd-driver/csv_filter.py \"' + attributes.join(';')  + '\" --path /cvi_identified.csv --output /cvi_identified_' + hospitalName + '_filtered.csv\n');
//     _exec('\tpython /mhmd-driver/csv_filter.py \"' + attributes.join(';')  + '\" --path /cvi_identified.csv --output /cvi_identified_' + hospitalName + '_filtered.csv', {stdio:[0,1,2],cwd: parent})
//     .then((buffer) => {
//         console.log('[NODE] Running CSV-Preprocessor');
//         console.log('\tpython /mhmd-driver/csv_preprocessor.py --path /cvi_identified_' + hospitalName + '_filtered.csv\n');
//         return _exec('python /mhmd-driver/csv_preprocessor.py --path /cvi_identified_' + hospitalName + '_filtered.csv', {stdio:[0,1,2],cwd: parent});
//     })
//     .then((buffer) => {
//         console.log('[NODE] Running XML-Generator');
//         console.log('\tpython /mhmd-driver/xml_generator.py /cvi_identified_' + hospitalName + '_filtered_edited.csv --table ' + hospitalName + '\n');
//         return _exec('python /mhmd-driver/xml_generator.py /cvi_identified_' + hospitalName + '_filtered_edited.csv --table ' + hospitalName, {stdio:[0,1,2],cwd: parent});
//     }).then((buffer) => {
//         console.log('[NODE] Running CSV-Importer');
//         console.log('\tsharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /cvi_identified_' + hospitalName + '_filtered_edited.csv --model /cvi_identified_' + hospitalName + '_filtered_edited.xml --separator c --log /cvi_identified_' + hospitalName + '_filtered_edited.log\n');
//         return _exec('sharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /cvi_identified_' + hospitalName + '_filtered_edited.csv --model /cvi_identified_' + hospitalName + '_filtered_edited.xml --separator c --log /cvi_identified_' + hospitalName + '_filtered_edited.log', {stdio:[0,1,2],cwd: parent});
//     }).then((result) => {
//         console.log('[NODE] Now unlinking intermidiate files.\n');
//         // remove intermidiate files
//         var unlink_promises = [];
//         unlink_promises.push( _unlinkIfExists(parent + '/cvi_identified_' + hospitalName + '_filtered.csv') );
//         unlink_promises.push( _unlinkIfExists(parent + '/cvi_identified_' + hospitalName + '_filtered_edited.csv') );
//         unlink_promises.push( _unlinkIfExists(parent + '/cvi_identified_' + hospitalName + '_filtered_edited.xml') );
//         unlink_promises.push( _unlinkIfExists(parent + '/cvi_identified_' + hospitalName + '_filtered_edited.log') );
//
//         return Promise.all(unlink_promises);
//     }).then((result) => {
//         console.log('[NODE] Data importing Successful.\n');
//         res.end();
//     }).catch((err) => {
//         console.log('[NODE] Failure on data importing.\n');
//         console.log(err);
//         res.status(400).send('Failure on data importing');
//     });
// });



app.listen(3000, () => console.log('MHMD-Driver app listening on port 3000!'));
