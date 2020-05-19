from gras.github.entity.api_static import APIStaticV4, EventStatic
from gras.github.entity.github_models import EventModel
from gras.github.github import GithubInterface
from local_settings import AUTH_KEY


class EventDetailStruct(GithubInterface, EventModel):
    """
        The object models the query to fetch the events of a repository and generates an object
        using
        :class:`gras.github.entity.github_models.EventModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `issue-timeline-items connection documentation`_ ,
        `pullrequest-timeline-items connection documentation`_ , `node documentation`_ , `assigned event
        documentation`_ , `cross-referenced event documentation`_ , `demilestoned event documentation`_ ,
        `labeled event documentation`_ , `marked-as-duplicate event documentation`_ , `mentioned event documentation`_ ,
        `milestoned event documentation`_ , `pinned event documentation`_ , `referenced event documentation`_ ,
        `renamed-title event documentation`_ , `reopened event documentation`_ , `transferred event documentation`_ ,
        `unassigned event documentation`_ , `unlabeled event documentation`_ , `unmarked-as-duplicate event
        documentation`_ , `unpinned event documentation`_
        for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _issue-timeline-items connection documentation:
            https://developer.github.com/v4/object/issuetimelineitemsconnection/

        .. _pullrequest-timeline-items connection documentation:
            https://developer.github.com/v4/object/issuetimelineitemsconnection/

        .. _node documentation:
            https://developer.github.com/v4/interface/node/

        .. _assigned event documentation:
            https://developer.github.com/v4/object/assignedevent/

        .. _cross-referenced event documentation:
            https://developer.github.com/v4/object/crossreferencedevent/

        .. _demilestoned event documentation:
            https://developer.github.com/v4/object/demilestonedevent/

        .. _labeled event documentation:
            https://developer.github.com/v4/object/labeledevent/

        .. _marked-as-duplicate event documentation:
            https://developer.github.com/v4/object/markedasduplicateevent/

        .. _mentioned event documentation:
            https://developer.github.com/v4/object/mentionedevent/

        .. _milestoned event documentation:
            https://developer.github.com/v4/object/milestonedevent/

        .. _pinned event documentation:
            https://developer.github.com/v4/object/pinnedevent/

        .. _referenced event documentation:
            https://developer.github.com/v4/object/referencedevent/

        .. _renamed-title event documentation:
            https://developer.github.com/v4/object/renamedtitleevent/

        .. _reopened event documentation:
            https://developer.github.com/v4/object/reopenedevent/

        .. _transferred event documentation:
            https://developer.github.com/v4/object/transferredevent/

        .. _unassigned event documentation:
            https://developer.github.com/v4/object/unassignedevent/

        .. _unlabeled event documentation:
            https://developer.github.com/v4/object/unlabeledevent/

        .. _unmarked-as-duplicate event documentation:
            https://developer.github.com/v4/object/unmarkedasduplicateevent/

        .. _unpinned event documentation:
            https://developer.github.com/v4/object/unpinnedevent/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
        :param type_filter: type of event
        :type type_filter: str
        :param since: date after which events should be fetched
        :type since: :class:`datetime.datetime` object
        :param number: the event number
        :type number: int
    """

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
        """Constructor Method"""
        super().__init__(
            query=self.QUERY,
            query_params=dict(name=name, owner=owner, type_filter=type_filter, number=number,
                              since="\"" + since + "\"" if since else "null")
        )

        self.type_filter = type_filter
        self.issue_number = number

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.event_struct.EventDetailStruct`. For more
            information see
            :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

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
        """
            generates a :class:`gras.github.entity.github_models.EventModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.EventModel` object
            :rtype: class
        """
        for lst in self.iterator():
            for node in lst:
                yield self.object_decoder(node, number=self.issue_number)


if __name__ == '__main__':
    e = EventDetailStruct(owner='tensorflow', name='tensorflow', type_filter='issue', since=None, number=22)
    
    it = 1
    for i in e.process():
        print(it)
        it += 1
