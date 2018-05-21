var SIMULATION_MODE = false;
process.argv.forEach(function (val, index, array) {
    if (val == '-sim' || val == '--sim' || val == '-simulation' || val == '--simulation') {
        SIMULATION_MODE = true;
    }
});

if (SIMULATION_MODE) {
    console.log('\n[NODE] Running in simulation mode\n');
} else {
    console.log('\n[NODE] Running within Docker\n');
}

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


app.post('/smpc/import', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);

    var configuration = req.body.attribute;
    console.log('[NODE] Going to import dataset for attribute ' + configuration + '\n');
    // file_name = file.substring(0, file.lastIndexOf('.')); // remove extension of file
    
    json_directory = '/patient_files';
    file_name = '/data.csv';
    
    console.log('[NODE] Running CSV-preprocessor.');
    console.log('\tpython /mhmd-driver/mesh_json_to_csv.py \"' + configuration  + '\"\n');
    
    _exec('python /mhmd-driver/mesh_json_to_csv.py \"' + configuration + '\"', {stdio:[0,1,2],cwd: parent})
      .then((buffer) => {
          console.log('[NODE] Running XML-Generator');
          console.log('\tpython /mhmd-driver/xml_generator.py --path ' + file_name + '\n');
          // console.log('\tpython /mhmd-driver/xml_generator.py --path ' + file_name + '_edited.csv\n');
          return _exec('python /mhmd-driver/xml_generator.py --path ' + file_name, {stdio:[0,1,2],cwd: parent});
          // return _exec('python /mhmd-driver/xml_generator.py --path ' + file_name + '_edited.csv', {stdio:[0,1,2],cwd: parent});
      })
      .then((buffer) => {
          console.log('[NODE] Running CSV-Importer');
          console.log('\tsharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /data.csv --model /data.xml --separator c --log ' + file_name + '.log\n');
          // console.log('\tsharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv ' + file_name + '_edited.csv --model ' + file_name + '.xml --separator c --log ' + file_name + '.log\n');
          return _exec('sharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv /data.csv --model /data.xml --separator c --log ' + file_name + '_edited.log', {stdio:[0,1,2],cwd: parent});
          // return _exec('sharemind-csv-importer --force --conf /mhmd-driver/client/client.conf --mode overwrite --csv ' + file_name + '_edited.csv --model ' + file_name + '_edited.xml --separator c --log ' + file_name + '_edited.log', {stdio:[0,1,2],cwd: parent});
      })
      .then((result) => {
          console.log('[NODE] Data importing Successful.\n');
          res.end();
      })
      .catch((err) => {
          console.log('[NODE] Failure on data importing.\n');
          console.log(err);
          res.status(400).send('Failure on data importing');
      });

});


app.listen(3000, () => console.log('MHMD-Driver app listening on port 3000!'));
