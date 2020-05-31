function read_file(path) {
    let fs = require('fs');
    let content = null;

    fs.readFile(path, 'utf8', function (err, data) {
        if (err) throw err;
        content = data;
    });

    return content;
}
