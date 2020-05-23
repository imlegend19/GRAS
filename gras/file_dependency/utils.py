MAX_BYTES = 200


def is_python_file(path: str):
    """
    Function to determine whether a file is python file or not.
    
    :param path: path of the file
    :type path: str
    
    :return: whether the file is a valid python file or not
    :rtype: bool
    """
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


def lines_of_code_counter(file):
    line_count = 0
    blank_line_count = 0
    comment_line_count = 0
    comment_flag = '0'
    
    for line in file:
        line_count += 1
        if comment_flag == '1':
            comment_line_count += 1
        if not line.strip():
            blank_line_count += 1
        elif line.strip().startswith('#'):
            comment_line_count += 1
        elif line.strip().startswith("\"\"\"") or line.strip().endswith("\"\"\""):
            if comment_flag == '0':
                comment_flag = '1'
                comment_line_count += 1
            else:
                comment_flag = '0'
    
    effective_loc = line_count - blank_line_count - comment_line_count
    return effective_loc
