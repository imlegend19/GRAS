import json


def _parse_dict(dic, delimiter="\n"):
    lst = []

    for key, value in dic.items():
        if isinstance(value, list) or isinstance(value, tuple):
            value = json.dumps(list(value))
        elif isinstance(value, str):
            value = f'"{value}"'

        lst.append(f"{key}: {value}")

    return f",{delimiter}".join(lst)


def create_node(node_type, var_name=None, **kwargs):
    if not var_name:
        var_name = node_type.lower()

    query = f"""
        CREATE ({var_name}: {node_type} {{
            {_parse_dict(kwargs)}            
        }})
        RETURN ID({var_name})
    """

    return query


def create_relationship(id1, id2, label1, label2, relation):
    query = f"""
        MATCH (a: {label1}), (b: {label2})
        WHERE ID(a) = {id1} AND ID(b) = {id2}
        CREATE (a)-[r: {relation}]->(b)
    """

    return query


def create_labeled_relationship(id1, id2, label1, label2, relation, **kwargs):
    query = f"""
        MATCH (a: {label1}), (b: {label2})
        WHERE ID(a) = {id1} AND ID(b) = {id2}
        CREATE (a)-[r: {relation} {{ {_parse_dict(kwargs, delimiter=" ")} }}]->(b)
    """

    return query
