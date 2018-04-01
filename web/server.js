const express = require('express')
const app = express()
var path = require('path');
var bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
var frontend = __dirname + "/frontend/";

app.get('/', (req, res) => res.sendFile(path.join(frontend + 'index.html')));

app.post('/histogram', function(req, res) {
    console.log(req.body)
    res.end()
});


app.listen(3000, () => console.log('Example app listening on port 3000!'))