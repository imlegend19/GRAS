from gras.errors import QueryObjectError


class QueryObject:
    def __init__(self, raw=None, object_type=None, object_fields=None, children=None, alias=None,
                 inline_fragment=False):
        self.object_type = object_type
        self.object_fields = object_fields
        self.children = children
        self.raw = raw
        self.alias = alias
        self.inline_fragment = inline_fragment

        if self.object_type is None and self.raw is None:
            raise QueryObjectError(msg="`raw` or `object_type` have to be specified.")

        if not raw:
            self._build()
        else:
            lines = [x if x.strip() != '' else None for x in list(filter(''.__ne__, raw.splitlines()))]
            lines = list(filter(None.__ne__, lines))

            for i in range(len(lines)):
                if i == 0 or i == len(lines) - 1:
                    lines[i] = lines[i].strip()
                else:
                    lines[i] = "\t" + lines[i].strip()

            self.query = "\n".join(lines)

    @staticmethod
    def __formatted_string(object_, end=True):
        if isinstance(object_, QueryObject):
            if end:
                return "\n".join([f"\t{x}" for x in object_.__str__().splitlines()])
            else:
                return "\n".join([f"\t{x}" for x in object_.__str__().splitlines()]) + "\n"

        if end:
            return f"\t{object_}"
        else:
            return f"\t{object_}\n"

    def _build(self):
        if isinstance(self.object_type, type):
            self.object_type = "__typename"

        if self.alias:
            self.object_type = f"{self.alias}: {self.object_type}"

        if self.inline_fragment:
            self.object_type = f"... on {self.object_type}"

        if self.object_fields:
            self.query = self.object_type + "(" + ", ".join(
                '%s: %s' % (f, self.object_fields[f] if self.object_fields[f] is not None else "null") for f in
                self.object_fields.keys()) + ")"
        else:
            self.query = self.object_type

        if self.children:
            self.query += " {{\n"

            for i in range(len(self.children)):
                self.query += self.__formatted_string(self.children[i],
                                                      end=True if i == len(self.children) - 1 else False)

            self.query += "\n}}"

    def __str__(self):
        return self.query

    def aggregate(self, name=None):
        if name:
            final_query = f"{name} " + "{{\n"
        else:
            final_query = "{{\n"

        final_query += self.__formatted_string(self) + "\n}}"

        return final_query


def remove_alias(query, alias):
    alias += ":"
    lines = query.splitlines()

    alias_indent = None
    alias_index = None
    for i, line in enumerate(lines):
        if alias in line:
            alias_indent = len(line) - len(line.lstrip())
            alias_index = i
            break

    if "{{" in lines[alias_index]:
        lines.pop(alias_indent)

        index_to_pop = []
        for i in range(alias_index, len(lines)):
            indent = len(lines[i]) - len(lines[i].lstrip())
            if alias_indent < indent:
                index_to_pop.append(i)
            elif alias_indent == indent:
                index_to_pop.append(i)
                break
            else:
                break

        del lines[index_to_pop[0]: index_to_pop[-1] + 1]
    else:
        lines.pop(alias_indent)

    return "\n".join(lines)


if __name__ == '__main__':
    x1 = """
    pageInfo(for: 2254, after: {after}) {{
        endCursor
        hasNextPage
    }}
    """
    q = QueryObject(
        raw=x1
    ).aggregate()

    print(q)
