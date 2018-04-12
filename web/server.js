const express = require('express');
const app = express();
const { execSync } = require('child_process');
const fs = require('fs');
var path = require('path');
var bodyParser = require('body-parser');
var parse = require('csv-parse')
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
var frontend = __dirname + "/frontend/";
var visuals = __dirname + "/visuals/";
global.__basedir = __dirname;

app.get('/', function (req, res) {
     // buildHtml(req);
    res.sendFile(path.join(frontend + 'index.html'));
});

app.use(express.static(path.join(__dirname, 'frontend'))); // public/static files
app.use("/visuals", express.static(__dirname + '/visuals'));

var req_counter = 0; // count the requests and give each new request a new ID

app.post('/histogram', function(req, res) {
    var parent = path.dirname(__basedir);
    var content = JSON.stringify(req.body);
    console.log(content);
    req_counter++;
    fs.writeFileSync(parent+'/configuration_' + req_counter + '.json', content, 'utf8', function (err) {
        if (err) {
            return console.log(err);
        }

    });
    console.log("[NODE] Configuration file was saved.");
    
    execSync('python main_generator.py configuration_' + req_counter + '.json', {stdio:[0,1,2],cwd: parent}, (err, stdout, stderr) => {
        if (err) {
            console.error(`exec error: ${err}`);
            return;
        }
    });
    console.log("[NODE] Main generated.");
    
    fs.existsSync(parent+'/.histogram_main_' + req_counter + '.sb.src', function(exists) {
        if(exists){
            fs.unlinkSync(parent+'/.histogram_main_' + req_counter + '.sb.src', function(err){
                if(err){
                    return console.log(err);
                }
                console.log('file deleted successfully');
            });
        }
    });
    console.log("[NODE] Old .histogram_main.sb.src deleted.");
    
    execSync('./compile.sh histogram_main_' + req_counter + '.sc', {stdio:[0,1,2],cwd: parent}, (err, stdout, stderr) => {
        if (err) {
            console.error(`exec error: ${err}`);
            return;
        }
    });
    console.log("[NODE] Program compiled.");
    execSync('./run.sh histogram_main_' + req_counter + '.sb 2> out.txt', {stdio:[0,1,2],cwd: parent}, (err, stdout, stderr) => {
        if (err) {
            console.error(`exec error: ${err}`);
            return;
        }
    });
    console.log("[NODE] Program executed.");
    var result = execSync('python plot.py', {cwd: parent}, (err, stdout, stderr) => {
        if (err) {
            console.error(`exec error: ${err}`);
            return;
        }
    });
    console.log("[NODE] Plotting done.");
    var graph_name = result.toString();
    graph_name = graph_name.slice(0,-1);
    // res.sendFile(path.join(visuals + graph_name));
    res.send('visuals/' + graph_name);
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
                var field_name = rows[i]['Field']
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

        })
    })
};




app.listen(3000, () => console.log('Example app listening on port 3000!'))