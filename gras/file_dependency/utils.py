MAX_BYTES = 200


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


def lines_of_code_counter(file):
    line_count = 0
    blank_line_count = 0
    comment_line_count = 0
    comment_flag = '0'

    with open(file, 'r') as f:
        for line in f:
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
