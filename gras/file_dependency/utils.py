MAX_BYTES = 200
import sys
import os, os.path


def is_python_file(path: str):
    if path.endswith(".py"):
        try:
            with open(path, 'rb') as fp:
                content = fp.read(MAX_BYTES)
                if not content:
                    return False

            return True
        except IOError:
            return False
    else:
        return False


def lines_of_code_counter(dir, ext='.py'):
    """

    :param dir: path of the dir to parse
    :type dir: str

    :param ext: file extension eg:'.py'
    :type ext: str

    :return: `list`[0] contains {file_name: (effective line count, line count, blank line count, comment line
    count)...} and `list`[1] contatins (effective line count,...) of the entire root directory and sub directories
    :rtype: list
    """
    commentSymbol = '#'  # TODO: need options for other languages
    filesToCheck = []
    ret = []
    acceptableFileExtensions = ['.py', '.java']
    file_dict = {}

    if ext not in acceptableFileExtensions:
        print("Extension not accepted")
        return 0

    for root, _, files in os.walk(dir):
        for f in files:
            fullpath = os.path.join(root, f)
            if fullpath.endswith(ext) and f != '__init__.py':  # TODO: add for other languages
                for extension in acceptableFileExtensions:
                    if fullpath.endswith(extension):
                        filesToCheck.append(fullpath)

    if not filesToCheck:
        print("No {} files found".format(ext))

    line_count = 0
    blank_line_count = 0
    comment_line_count = 0

    for file in filesToCheck:
        with open(file, 'r') as f:
            f_linecount = 0
            f_blanklinecount = 0
            f_commentlinecount = 0

            for line in f:
                line_count += 1
                f_linecount += 1

                if not line.strip():
                    blank_line_count += 1
                    f_blanklinecount += 1
                elif line.strip().startswith(commentSymbol):
                    comment_line_count += 1
                    f_commentlinecount += 1
            f_effective_loc = f_linecount - f_blanklinecount - f_commentlinecount
            file_dict[os.path.basename(file)] = (f_effective_loc, f_linecount, f_blanklinecount, f_commentlinecount)

    effective_loc = line_count - blank_line_count - comment_line_count
    ret.append(file_dict)
    ret.append((effective_loc, line_count, blank_line_count, comment_line_count))

    return ret

    #

#
# ret = lines_of_code_counter('/home/viper/dev/GRAS/')
# print(ret[1][0], '\n', ret[0], '\n', "total file count", len(ret[0]))
