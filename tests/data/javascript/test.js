function read_file(path) {
    let fs = require('fs');
    let content = null;

    fs.readFile(path, 'utf8', function (err, data) {
        if (err) throw err;
        content = data;
    });

    return content;
}

const b = (b1, b2) => {
};

function testfile(t) {
    const test3 = 15;
}

var lol = 10;
const test = 12;
