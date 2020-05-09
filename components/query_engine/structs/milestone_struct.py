from components.query_engine.entity.api_static import APIStaticV4, MilestoneStatic
from components.query_engine.entity.github_models import MilestoneModel
from components.query_engine.github import GithubInterface


class MilestoneStruct(GithubInterface, MilestoneModel):
    MILESTONE_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                milestones(first: 100, after: {after}) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        creator {{
                            login
                        }}
                        number
                        description
                        dueOn
                        title
                        closedAt
                        createdAt
                        state
                        updatedAt
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=self.MILESTONE_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )
    
    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break
            
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                MilestoneStatic.MILESTONES][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
            
            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"
            
            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                MilestoneStatic.MILESTONES][APIStaticV4.NODES]
            
            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                        MilestoneStatic.MILESTONES][APIStaticV4.NODES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                                MilestoneStatic.MILESTONES][APIStaticV4.NODES],
                        )
                    )

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                MilestoneStatic.MILESTONES][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for ms in lst:
                yield self.object_decoder(ms)
