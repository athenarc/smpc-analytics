const express = require('express');
const app = express();
const { exec } = require('child_process');
const fs = require('fs');
var path = require('path');
var bodyParser = require('body-parser');
var parse = require('csv-parse');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
var frontend = __dirname + "/frontend/";
var visuals = __dirname + "/visuals/";
global.__basedir = __dirname;

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


app.post('/histogram', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;

    _writeFile(parent+'/configuration_' + req_counter + '.json', content, 'utf8')
        .then((buffer) => {
            console.log('[NODE] Request(' + req_counter + ') Configuration file was saved.\n');
            return _exec('python main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent});
        })
        .then((buffer) => {
            console.log('[NODE] Request(' + req_counter + ') Main generated.\n');
            return _unlinkIfExists(parent + '/.histogram_main_' + req_counter + '.sb.src');
        })
        .then((msg) => {
            console.log("[NODE] Old .histogram_main" + req_counter + ".sb.src deleted.\n");
            return _exec('./sm_compile_and_run.sh histogram_main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent});
        })
        .then((buffer) => {
            console.log('[NODE] Request(' + req_counter + ') Program executed.\n');
            return _exec('tail -n +`cut -d " "  -f "9-" /etc/sharemind/server.log  | grep -n "Starting process" | tail -n 1 | cut -d ":" -f 1` /etc/sharemind/server.log | cut -d " "  -f "9-" >  out_' + req_counter + '.txt', {stdio:[0,1,2],cwd: parent});
        })
        .then((buffer) => {
            return _exec('python plot.py ' + req_counter, {cwd: parent});
        })
        .then((result) => {
            console.log('[NODE] Request(' + req_counter + ') Plotting done.\n');
            var graph_name = result.toString();
            graph_name = graph_name.slice(0,-1);
            res.send('visuals/' + graph_name);
        })
        .catch((err) => {
            console.log(err);
        });

});


function buildHtml(req) {
    fs.readFile('cvi_summary.csv', function (err, fileData) {
        var form = `
<form action="/histogram" method="post">
    <p>
        <ul class="list-group">
`;
        parse(fileData, {columns: true, delimiter: ','}, function(err, rows) {
            for (var i = 0; i < rows.length; i++) {
                var field_name = rows[i].Field;
                form = form + `
             <li class="list-group-item">
                <input type="checkbox" name="attributes" value="`+ field_name +`"> ` + field_name + ` &ensp;
                <span style="float:right;"><input type="number" id="`+ field_name +`Cells" name="cells" min="1" max="15" style="display:none;"></span>
            </li>
`;
            }
            form = form + `
        </ul>
    </p>
    <p>
        <input type="submit" class="btn btn-info" value="Compute Histogram(s)">
    </p>
</form>
`;

            fs.writeFile(frontend+'form.html', form, function(err) {
                if(err) {
                    return console.log(err);
                }
                console.log("[NODE] form.html saved.");
            });

        });
    });
}



app.listen(3000, () => console.log('Example app listening on port 3000!'));