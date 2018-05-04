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

    var file = req.body.file;
    console.log('[NODE] Importing dataset: ' + file + '\n');
    file_name = file.substring(0, file.lastIndexOf('.')); // remove extension of file
    
    _exec('python dataset-scripts/xml_generator.py --path ' + file, {stdio:[0,1,2],cwd: parent})
      .then((buffer) => {
          console.log('[NODE] XML file created from ' + file + '\n');
          console.log('[NODE] Running CSV-Importer\n');
          return _exec('yes | sharemind-csv-importer --conf client/client.conf --mode overwrite --csv ' + file + ' --model ' + file_name + '.xml --separator c --log ' + file_name + '.log', {stdio:[0,1,2],cwd: parent});
      })
      .then((result) => {
          console.log('[NODE] Response ready.\n');
          res.send(file.toString());
      })
      .catch((err) => {
          console.log(err);
      });

});


app.listen(3000, () => console.log('MHMD-Driver app listening on port 3000!'));
