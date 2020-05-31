from gras.github.entity.api_static import APIStaticV4, MilestoneStatic
from gras.github.entity.github_models import MilestoneModel
from gras.github.github import GithubInterface


class MilestoneStruct(GithubInterface, MilestoneModel):
    """
        The object models the query to fetch the list of milestones associated with a repository and generates an
        object using
        :class:`gras.github.entity.github_models.MilestoneModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `milestone connection documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _milestone connection documentation:
            https://developer.github.com/v4/object/milestoneconnection/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

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

    def __init__(self, name, owner):
        """Constructor method
        """
        super().__init__(
            query=self.MILESTONE_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.milestone_struct.MilestoneStruct`. For more information
            see
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
        """
        generates a :class:`gras.github.entity.github_models.MilestoneModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.MilestoneModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for ms in lst:
                yield self.object_decoder(ms)
