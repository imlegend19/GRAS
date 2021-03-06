from gras.errors import StructError
from gras.github.entity.api_static import APIStaticV4, EventStatic
from gras.github.entity.github_models import EventModel
from gras.github.github import GithubInterface


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

    ISSUE_EVENT_TYPES = "ASSIGNED_EVENT, CROSS_REFERENCED_EVENT, DEMILESTONED_EVENT, LABELED_EVENT, " \
                        "MARKED_AS_DUPLICATE_EVENT, MENTIONED_EVENT, UNPINNED_EVENT, MILESTONED_EVENT, PINNED_EVENT, " \
                        "REFERENCED_EVENT, RENAMED_TITLE_EVENT, REOPENED_EVENT, TRANSFERRED_EVENT, UNASSIGNED_EVENT, " \
                        "UNLABELED_EVENT, UNMARKED_AS_DUPLICATE_EVENT, CLOSED_EVENT"

    ISSUE_EVENTS = """
        
        ... on AssignedEvent {
            who: actor {
                login
            }
            when: createdAt
            added: assignee {
                ... on User {
                    login
                }
            }
        }
        ... on ClosedEvent {
            who: actor {
                login
            }
            when: createdAt
            added: closer {
                type: __typename
                ... on Commit {
                    oid
                }
                ... on PullRequest {
                    number
                }
            }
        }
        ... on CrossReferencedEvent {
            who: actor {
                login
            }
            when: referencedAt
            isCrossRepository
            added: source {
                type: __typename
                ... on Issue {
                    number
                }
                ... on PullRequest {
                    number
                }
            }
        }
        ... on DemilestonedEvent {
            who: actor {
                login
            }
            when: createdAt
            removed: milestoneTitle
        }
        ... on LabeledEvent {
            who: actor {
                login
            }
            when: createdAt
            added: label {
                name
            }
        }
        ... on MarkedAsDuplicateEvent {
            who: actor {
                login
            }
            when: createdAt
        }
        ... on MentionedEvent {
            who: actor {
                login
            }
            when: createdAt
        }
        ... on MilestonedEvent {
            who: actor {
                login
            }
            when: createdAt
            added: milestoneTitle
        }
        ... on PinnedEvent {
            who: actor {
                login
            }
            when: createdAt
        }
        ... on ReferencedEvent {
            who: actor {
                login
            }
            when: createdAt
            isCrossRepository
            added: commit {
                oid
            }
        }
        ... on RenamedTitleEvent {
            who: actor {
                login
            }
            when: createdAt
            removed: previousTitle
            added: currentTitle
        }
        ... on ReopenedEvent {
            who: actor {
                login
            }
            when: createdAt
        }
        ... on TransferredEvent {
            who: actor {
                login
            }
            when: createdAt
            removed: fromRepository {
                name
                owner {
                    login
                }
            }
        }
        ... on UnassignedEvent {
            who: actor {
                login
            }
            when: createdAt
        }
        ... on UnlabeledEvent {
            who: actor {
                login
            }
            when: createdAt
            removed: label {
                name
            }
        }
        ... on UnmarkedAsDuplicateEvent {
            who: actor {
                login
            }
            when: createdAt
        }
        ... on UnpinnedEvent {
            who: actor {
                login
            }
            when: createdAt
        }
    """

    PULL_REQUEST_EVENT_TYPES = "CONVERT_TO_DRAFT_EVENT, MERGED_EVENT, REVIEW_REQUESTED_EVENT"

    PULL_REQUEST_EVENTS = """
        ... on ConvertToDraftEvent {
            who: actor {
                login
            }
            when: createdAt
        }
        ... on MergedEvent {
            who: actor {
                login
            }
            removed: commit {
                oid
            }
            when: createdAt
            added: mergeRefName
        }
        ... on ReviewRequestedEvent {
            who: actor {
                login
            }
            when: createdAt
            added: requestedReviewer {
                ... on User {
                    login
                }
            }
        }
    """

    QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                {type_filter}(number: {number}) {{
                    timelineItems(first:250, itemTypes:[{event_types}], since: {since}, after: {after}) {{
                        totalCount
                        pageInfo {{
                            endCursor
                            hasNextPage
                        }}
                        nodes {{
                            eventType: __typename
                            {events}
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
                              event_types=self.ISSUE_EVENT_TYPES if type_filter == "issue" else
                              self.ISSUE_EVENT_TYPES + ', ' + self.PULL_REQUEST_EVENT_TYPES,
                              events=self.ISSUE_EVENTS if type_filter == "issue" else
                              self.ISSUE_EVENTS + self.PULL_REQUEST_EVENTS,
                              since="\"" + since + "\"" if since else "null", after="null")
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
                try:
                    yield self.object_decoder(node, number=self.issue_number)
                except Exception as e:
                    raise StructError(msg=f"({__class__.__name__}) {e}")
