import json


def _parse_dict(dic):
    lst = []

    for key, value in dic.items():
        if isinstance(value, list) or isinstance(value, tuple):
            value = json.dumps(list(value))
        elif isinstance(value, str):
            value = f'"{value}"'

        lst.append(f"{key}: {value}")

    return ",\n".join(lst)


def create_node(var_name, node_type, **kwargs):
    query = f"""
        CREATE ({var_name}: {node_type} {{
            {_parse_dict(kwargs)}            
        }})
    """

    return query
