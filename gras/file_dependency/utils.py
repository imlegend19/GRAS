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
