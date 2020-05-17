import unittest

from gras.github.query_builder import QueryObject
from gras.github.structs.language_struct import LanguageStruct


class TestQueryObject(unittest.TestCase):
    def test_language_struct_query(self):
        query = QueryObject(
            object_type="repository",
            object_fields=dict(name="\"{name}\"", owner="\"{owner}\""),
            children=[
                QueryObject(
                    object_type="languages",
                    object_fields=dict(first=100, orderBy="{{ field: SIZE, direction: ASC }}", after="{after}"),
                    children=[
                        QueryObject(
                            object_type="edges",
                            children=[
                                "size",
                                QueryObject(
                                    object_type="node",
                                    children=["name"]
                                )
                            ]
                        ),
                        QueryObject(
                            object_type="pageInfo",
                            children=[
                                "endCursor",
                                "hasNextPage"
                            ]
                        )
                    ]
                )
            ]
        ).aggregate()
        
        self.assertEqual([x.strip() for x in query.strip().splitlines()],
                         [x.strip() for x in LanguageStruct.LANGUAGE_QUERY.strip().splitlines()])
