from gras.github.entity.api_static import APIStaticV3, APIStaticV4, CommitStatic
from gras.github.entity.github_models import CodeChangeModel, CommitModelV3, CommitModelV4, deprecated
from gras.github.github import GithubInterface


class CodeChangeStruct(GithubInterface, CodeChangeModel):
    """
        The object models the query to fetch code change data of a commit in a repository and
        generates an object using :class:`gras.github.entity.github_models.CodeChangeModel` containing the
        fetched data.

        Please see GitHub's `single-commit documentation`_ for more information.

        .. _single-commit documentation:
            https://developer.github.com/v3/repos/commits/#get-a-single-commit

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

        :param commit_id: id of the commit
        :type commit_id: str
    """

    def __init__(self, name, owner, commit_id):
        """Constructor Method"""
        super().__init__(
            query=None,
            url=f"https://api.github.com/repos/{owner}/{name}/commits/{commit_id}",
            query_params=None
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.commit_struct.CodeChangeStruct`. For more
            information see :class:`gras.github.github.githubInterface`.
            
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """
    
        generator = self._generator()
        return next(generator).json()[CommitStatic.FILES]

    def process(self):
        """
            Generates a :class:`gras.github.entity.github_models.CodeChangeModel` object representing the fetched data.
            
            :return: A :class:`gras.github.entity.github_models.CodeChangeModel` object
            :rtype: class
        """

        for cc in self.iterator():
            obj = self.object_decoder(cc)
            if obj:
                yield obj


@deprecated("Please use :class:`~CommitStructV4` instead.")
class CommitStructV3(GithubInterface, CommitModelV3):
    """
        The object models the query to fetch commits in a repository and generates an object using
        :class:`gras.github.entity.github_models.CommitModelV3` containing the fetched data.

        Please see GitHub's `commit documentation`_ for more
        information.

        .. _commit documentation:
            https://developer.github.com/v3/repos/commits/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

        :param start_date: fetch data after this date
        :type start_date: :class:`datetime.datetime` object

        :param end_date: fetch data till this date
        :type end_date: :class:`datetime.datetime` object

        :param merge: `True` if commit is a merge commit, `False` otherwise
        :type merge: bool
    """

    def __init__(self, name, owner, start_date, end_date, merge):
        """Constructor Method"""
        super().__init__(
            query=None,
            url=f"https://api.github.com/search/commits?q=repo:{owner}/{name}+merge:{merge}+"
                f"committer-date:{start_date}..{end_date}+sort:committer-date-asc&per_page=100&page=1",
            query_params=None,
            additional_headers=dict(Accept="application/vnd.github.cloak-preview+json")
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.commit_struct.CommitStructV3`. For more information see
            :class:`gras.github.github.githubInterface`.
            
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """
    
        generator = self._generator()
        hasNextPage = True
    
        while hasNextPage:
            response = next(generator)  # Response object (not json)

            try:
                next_url = response.links["next"]["url"]
            except KeyError:
                break

            self.url = next_url

            response = response.json()
            yield response[APIStaticV3.ITEMS]

            hasNextPage = True if next_url is not None else False


class CommitStructV4(GithubInterface, CommitModelV4):
    """
        The object models the query to fetch commits in a branch in a repository and generates an object using
        :class:`gras.github.entity.github_models.CommitModelV4` containing the fetched data.

        Please see GitHub's `repository documentation`_ , `gitObject documentation`_ ,
        `commit-history documentation`_ , `node documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _gitObject documentation:
            https://developer.github.com/v4/interface/gitobject/

        .. _commit-history documentation:
            https://developer.github.com/v4/object/commithistoryconnection/

        .. _node documentation:
            https://developer.github.com/v4/interface/node/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

        :param start_date: fetch data after this date
        :type start_date: :class:`datetime.datetime` object

        :param end_date: fetch data till this date
        :type end_date: :class:`datetime.datetime` object

        :param branch: name of the branch
        :type branch: str

        :param after: return the elements in the list that come after the specified cursor `after`
        :type after: str

        :param oid: Git Object ID
        :type oid: GitObjectID
    """

    COMMIT_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                object(expression: "{branch}") {{
                    ... on Commit {{
                        history(since: "{start_date}", until: "{end_date}", first: 100, after: {after}) {{
                            totalCount
                            pageInfo {{
                                hasNextPage
                                endCursor
                            }}
                            nodes {{
                                oid
                                additions
                                deletions
                                author {{
                                    email
                                    name
                                    user {{
                                        login
                                    }}
                                }}
                                authoredDate
                                committer {{
                                    email
                                    name
                                    user {{
                                        login
                                    }}
                                }}
                                committedDate
                                message
                                status {{
                                    state
                                }}
                                changedFiles
                                parents {{
                                    totalCount
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """

    SINGLE_COMMIT_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                object(oid: "{oid}") {{
                    ... on Commit {{
                        oid
                        additions
                        deletions
                        author {{
                            email
                            name
                            user {{
                                login
                            }}
                        }}
                        authoredDate
                        committer {{
                            email
                            name
                            user {{
                                login
                            }}
                        }}
                        committedDate
                        message
                        status {{
                            state
                        }}
                        changedFiles
                        parents {{
                            totalCount
                        }}
                    }}
                }}
            }}
        }}
    """

    def __init__(self, name, owner, start_date=None, end_date=None, branch=None, after="null", oid=None,
                 github_token=None):
        """Constructor Method"""
        super().__init__(
            query=self.SINGLE_COMMIT_QUERY if oid else self.COMMIT_QUERY,
            query_params=dict(name=name, owner=owner, oid=oid) if oid else dict(name=name, owner=owner, after=after,
                                                                                start_date=start_date,
                                                                                end_date=end_date, branch=branch),
            github_token=github_token
        )
    
        self.oid = oid

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.commit_struct.CommitStructV4`. For more information see
            :class:`gras.github.github.githubInterface`.
            
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        hasNextPage = True

        if not self.oid:
            while hasNextPage:
                try:
                    response = next(generator)
                except StopIteration:
                    break

                try:
                    endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][
                        CommitStatic.HISTORY][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
                except KeyError:
                    endCursor = None

                self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

                try:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][CommitStatic.HISTORY][
                        APIStaticV4.NODES]
                except KeyError:
                    yield None

                try:
                    hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][
                        CommitStatic.HISTORY][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]
                except KeyError:
                    hasNextPage = False
        else:
            response = next(generator)
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT]

    def process(self):
        """
            Generates a :class:`gras.github.entity.github_models.CommitModelV4` object representing the fetched data.
            
            :return: A :class:`gras.github.entity.github_models.CommitModelV4` object
            :rtype: class
        """

        if not self.oid:
            for lst in self.iterator():
                for commit in lst:
                    yield self.object_decoder(commit)
        else:
            for dic in self.iterator():
                yield self.object_decoder(dic)
