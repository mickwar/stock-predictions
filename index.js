const http = require('http');
const path = require('path');
const fs = require('fs');
const spawn = require('child_process').spawn;


var APIKEY = "";
var SYMBOL = "";

var lower = "0.0";
var mean  = "0.0";
var upper = "0.0";

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

    // read the html file and then send to browser (i.e. load a page)
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
    // TODO request seems to send on page reload
    // (this might be intentional behavior, to resend form submission on reload
    if (request.method === 'POST'){
        var data = '';

        request.on('data', function(chunk) {
            data += chunk;
            });

        request.on('end', function() {
            // parse the data
            APIKEY = data.substring(data.indexOf("=") + 1, data.indexOf("&"));
            SYMBOL = data.substring(data.lastIndexOf("=") + 1, data.length);
            callPython(APIKEY, SYMBOL);
            });
        }

    });

callPython = function(APIKEY, SYMBOL){
    // Provide default values of left blank
    APIKEY = APIKEY === "" ? "default" : APIKEY;
    SYMBOL = SYMBOL === "" ? "AMZN" : SYMBOL;

    // Start the process which loads the virtual environment and
    // executes the python script, passing the key and symbol as arguments
    const pyProc = spawn('bash', ['run_python.sh', APIKEY, SYMBOL]);

    // Process the output
    pyProc.stdout.on('data', (data) => {
        // data.toString();
        let tmp = data.toString().split('\n');
        lower = tmp[0];
        mean = tmp[1];
        upper = tmp[2];
        // document.getElementById("predLower").innerText = lower;
        // document.getElementById("predMean").innerText = mean;
        // document.getElementById("predUpper").innerText = upper;
        console.log(lower);
        console.log(mean);
        console.log(upper);
        });
    }


// check if environment variable PORT is found and use that value,
// otherwise default to 5000
const PORT = process.env.PORT || 5000;

server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
