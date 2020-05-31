const { program } = require('commander');

function read_file(path) {
    return require('fs').readFileSync(path, 'utf8');
}

function parse(path) {
    let esprima = require('esprima');

    let content = read_file(path);
    let ast = esprima.parse(content, { jsx: true, loc: true, comment: true });
    console.log(JSON.stringify(ast, null, 4));
}

program
    .usage('<file>')
    .action((file) => {
        parse(file.args.pop());
    })
    .parse(process.argv);
