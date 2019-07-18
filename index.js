const http = require('http');
const path = require('path');
const fs = require('fs');
const spawn = require('child_process').spawn;


const server = http.createServer((request, response) => {
    // build file path
    // ternary operator, a ? b : c, "if a is true, then b, else c"
    let filePath = path.join(
        __dirname,
        'public',
        request.url === '/' ? 'index.html' : request.url
        );

    // extension of file
    let extname = path.extname(filePath);

    // initial content type
    let contentType = 'text/html';

    // check extension to set content type
    switch(extname) {
        case '.js':
            contentType = 'text/javascript';
            break;
        case '.css':
            contentType = 'text/css';
            break;
        case '.json':
            contentType = 'application/json';
            break;
        case '.png':
            contentType = 'image/png';
            break;
        case '.jpg':
            contentType = 'image/jpg';
            break;
        }

    fs.readFile(
        filePath,
        (err, content) => {
            if (err) {
                if (err.code == 'ENOENT'){
                    // page not found
                    fs.readFile(path.join(__dirname, 'public', '404.html'),
                        (err, content) => {
                        response.writeHead(200, { 'Content-Type': 'text/html' });
                        response.end(content, 'utf8');
                        });
                } else {
                    // probably a server error (5xx code)
                    response.writeHead(500);
                    response.end(`Server error: ${err.code}`);
                    }
            } else {
                // write to headers
                response.writeHead(200, { 'Content-Type': contentType });
                response.end(content);
                }
        });

    // handle button click
    // TODO request seems to send on page re-load
    if (request.method === 'POST'){
        var data = '';

        request.on('data', function(chunk) {
            data += chunk;
            });

        request.on('end', function() {
            // parse the data
            var APIKEY = data.substring(data.indexOf("=") + 1, data.indexOf("&"));
            var SYMBOL = data.substring(data.lastIndexOf("=") + 1, data.length);
            callPython(data);
            });
        }

    });

callPython = function(input){
    // virtual env?
    // const pyProc = spawn('source env/bin/activate');
    const pyProc = spawn('python', ['python/test.py']);
    pyProc.stdout.on('data', (data) => {
        console.log(data.toString());
        });
    console.log("function called");
    }


// check if environment variable PORT is found and use that value,
// otherwise default to 5000
const PORT = process.env.PORT || 5000;

server.listen(PORT, () => console.log(`Server running on port ${PORT}`));

//const endpoint = "https://www.alphavantage.co/query";
//const params = ["function={}", "symbol={}", "outputsize={}", "datatype={}", "apikey={}"].join("&");
//const call = endpoint + "?" + params.format("TIME_SERIES_DAILY_ADJUSTED",
//    symbols[i], outputsize, "csv", APIKEY)

