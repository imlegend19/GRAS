from gras.github.entity.api_static import APIStaticV4, EventStatic
from gras.github.entity.github_models import EventModel
from gras.github.github import GithubInterface
from local_settings import AUTH_KEY


class EventDetailStruct(GithubInterface, EventModel):
    QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                {type_filter}(number: {number}) {{
                    timelineItems(first:250, itemTypes:[ASSIGNED_EVENT, CROSS_REFERENCED_EVENT, DEMILESTONED_EVENT,
                                        LABELED_EVENT, MARKED_AS_DUPLICATE_EVENT, MENTIONED_EVENT, UNPINNED_EVENT,
                                        MILESTONED_EVENT, PINNED_EVENT, REFERENCED_EVENT, RENAMED_TITLE_EVENT,
                                        REOPENED_EVENT, TRANSFERRED_EVENT, UNASSIGNED_EVENT, UNLABELED_EVENT,
                                        UNMARKED_AS_DUPLICATE_EVENT], since: {since}, after: {after}) {{
                        totalCount
                        pageInfo {{
                            endCursor
                            hasNextPage
                        }}
                        nodes {{
                            eventType: __typename
                            ... on AssignedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                added: assignee {{
                                    ... on User {{
                                        login
                                    }}
                                }}
                            }}
                            ... on CrossReferencedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: referencedAt
                                isCrossRepository
                                added: source {{
                                    type: __typename
                                    ... on Issue {{
                                        number
                                    }}
                                    ... on PullRequest {{
                                        number
                                    }}
                                }}
                            }}
                            ... on DemilestonedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                removed: milestoneTitle
                            }}
                            ... on LabeledEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                added: label {{
                                    name
                                }}
                            }}
                            ... on MarkedAsDuplicateEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                            }}
                            ... on MentionedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                            }}
                            ... on MilestonedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                added: milestoneTitle
                            }}
                            ... on PinnedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                            }}
                            ... on ReferencedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                isCrossRepository
                                added: commit {{
                                    oid
                                }}
                            }}
                            ... on RenamedTitleEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                removed: previousTitle
                                added: currentTitle
                            }}
                            ... on ReopenedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                            }}
                            ... on TransferredEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                removed: fromRepository {{
                                    name
                                    owner {{
                                        login
                                    }}
                                }}
                            }}
                            ... on UnassignedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                            }}
                            ... on UnlabeledEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                                removed: label {{
                                    name
                                }}
                            }}
                            ... on UnmarkedAsDuplicateEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                            }}
                            ... on UnpinnedEvent {{
                                who: actor {{
                                    login
                                }}
                                when: createdAt
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, owner, name, type_filter, since, number):
        super().__init__(
            query=self.QUERY,
            query_params=dict(name=name, owner=owner, type_filter=type_filter, number=number,
                              since="\"" + since + "\"" if since else "null", after="null"),
            github_token=AUTH_KEY
        )

        self.type_filter = type_filter
        self.issue_number = number
    
    def iterator(self):
        generator = self._generator()
        hasNextPage = True
    
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break
        
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][
                EventStatic.TIMELINE_ITEMS][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
        
            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"
        
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][
                EventStatic.TIMELINE_ITEMS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][
                EventStatic.TIMELINE_ITEMS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for node in lst:
                yield self.object_decoder(node, number=self.issue_number)


if __name__ == '__main__':
    e = EventDetailStruct(owner='tensorflow', name='tensorflow', type_filter='issue', since=None, number=22)
    
    it = 1
    for i in e.process():
        print(it)
        it += 1
