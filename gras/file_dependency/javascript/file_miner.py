import subprocess

if __name__ == '__main__':
    # Installing npm dependencies
    subprocess.run(['npm', 'install'])
    
    PATH = "/home/mahen/PycharmProjects/GRAS/gras/file_dependency/javascript/esprima-parser.js"
    
    out = subprocess.run(['node', 'esprima-parser.js', PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(out.stdout.decode('utf-8'))
