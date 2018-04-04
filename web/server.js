const express = require('express')
const app = express()
const { execSync } = require('child_process');
const fs = require('fs');
var path = require('path');
var bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'frontend'))) // public/static files
app.use(bodyParser.urlencoded({ extended: true }));
var frontend = __dirname + "/frontend/";
var visuals = __dirname + "/visuals/";
global.__basedir = __dirname;

app.get('/', (req, res) => res.sendFile(path.join(frontend + 'index.html')));

app.post('/histogram', function(req, res) {
    var parent = path.dirname(__basedir)
    const content = JSON.stringify(req.body);
    fs.writeFileSync(parent+'/configuration.json', content, 'utf8', function (err) {
        if (err) {
            return console.log(err);
        }

    });
    console.log("[NODE] Configuration file was saved.");
    execSync('python main_generator.py configuration.json', {stdio:[0,1,2],cwd: parent}, (err, stdout, stderr) => {
        if (err) {
            console.error(`exec error: ${err}`);
            return;
        }
    });
    console.log("[NODE] Main generated.");
    fs.existsSync(parent+'/.histogram_main.sb.src', function(exists) {
        if(exists){
            fs.unlinkSync(parent+'/.histogram_main.sb.src', function(err){
                if(err){
                    return console.log(err);
                }
                console.log('file deleted successfully');
            });
        }
    });
    console.log("[NODE] Old .histogram_main.sb.src deleted.");
    execSync('./compile.sh histogram_main.sc', {stdio:[0,1,2],cwd: parent}, (err, stdout, stderr) => {
        if (err) {
            console.error(`exec error: ${err}`);
            return;
        }
    });
    console.log("[NODE] Program compiled.");
    execSync('./run.sh histogram_main.sb 2> out.txt', {stdio:[0,1,2],cwd: parent}, (err, stdout, stderr) => {
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
    res.sendFile(path.join(visuals +graph_name));
});


app.listen(3000, () => console.log('Example app listening on port 3000!'))