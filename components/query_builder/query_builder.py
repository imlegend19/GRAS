from pprint import pprint
class QueryBuilder():
    def __init__(self, query = '',alias_list={}):
        self.query = query
        self.alias_list = alias_list
    
    def remove_duplicate_spaces(self, query):
        return " ".join(query.split())    

    def append_alias(self):
        query = '{{ ' + self.query
        for alias in self.alias_list:
            query = query + ' {{ ' + alias_list[alias]
        query = query + ' }}'
        return self.remove_duplicate_spaces(query)

    def remove_alias(self,alias:str):
        del self.alias_list[alias]
        return self.append_alias()
        
          
#======================================
# TESTING
#=====================================

LANGUAGE_QUERY = """repository(name: "{name}", owner: "{owner}")"""

alias_list = {
    'language' : """languages: languages(first: 100, orderBy: {{ field: SIZE, direction: ASC }}, after: {after}) {{
                    edges {{
                        size
                        node {{
                            name
                        }}
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}""",
    'stargazer' : """stargazers: stargazers(first: 100, orderBy: {{ field: STARRED_AT, direction:ASC }}, after: {after}) {{
                    edges {{
                        starredAt
                        node {{
                            login
                            id
                        }}
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }} """
}
q = QueryBuilder(LANGUAGE_QUERY, alias_list).append_alias()
pprint(q)
print("\n")
Q = QueryBuilder(LANGUAGE_QUERY, alias_list).remove_alias('stargazer')
pprint(Q)
#print("".join(alias_list[0].split()))


    
    
