class BaseStatic(type):
    def __setattr__(self, name, value):
        raise ValueError("Cannot change the value of a read-only variable.")


class APIStaticV4(metaclass=BaseStatic):
    BASE_URL = "https://api.github.com/graphql"
    NAME = "name"
    DATA = "data"
    RESOURCE = "resource"
    ID = "id"
    LOGIN = "login"
    TOTAL_COUNT = "totalCount"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    PAGE_INFO = "pageInfo"
    HAS_NEXT_PAGE = "hasNextPage"
    END_CURSOR = "endCursor"
    NODES = "nodes"
    NODE = "node"
    EDGES = "edges"
    CREATOR = "creator"
    URL = "url"
    DESCRIPTION = "description"
    REPOSITORY = "repository"
    AFTER = "after"
    WATCHERS = "watchers"
    SEARCH = "search"
    NUMBER = "number"
    OID = "oid"


class APIStaticV3(metaclass=BaseStatic):
    INCOMPLETE_RESULTS = "incomplete_results"
    ITEMS = "items"
    TOTAL_COUNT = "total_count"
    LOGIN = "login"
    NAME = "name"
    DATE = "date"
    EMAIL = "email"


class CommitStatic(metaclass=BaseStatic):
    AUTHOR = "author"
    COMMIT = "commit"
    COMMITTER = "committer"
    MESSAGE = "message"
    SHA = "sha"


class RepositoryStatic(metaclass=BaseStatic):
    REPOSITORY = "repository"
    DISK_USAGE = "diskUsage"
    FORK_COUNT = "forkCount"
    HOMEPAGE_URL = "homepageUrl"
    IS_ARCHIVED = "isArchived"
    IS_FORK = "isFork"
    OWNER = "owner"
    PRIMARY_LANGUAGE = "primaryLanguage"
    STARGAZERS = "stargazers"
    WATCHERS = "watchers"
    STARRED_AT = "starredAt"
    REFS = "refs"
    TARGET = "target"
    LANGUAGES = "languages"
    SIZE = "size"


class MilestoneStatic(metaclass=BaseStatic):
    MILESTONES = "milestones"
    DUE_ON = "dueOn"
    TITLE = "title"
    CLOSED_AT = "closedAt"
    STATE = "state"
    CREATOR = "creator"


class LabelStatic(metaclass=BaseStatic):
    LABELS = "labels"
    COLOR = "color"


class IssueStatic(metaclass=BaseStatic):
    COMMITS = "commits"
    PULL_REQUEST = "pullRequest"
    FILES = "files"
    STATE = "state"
    REACTIONS = "reactions"
    LABELS = "labels"
    ASSIGNEES = "assignees"
    ISSUE = "issue"
    TITLE = "title"
    BODY_TEXT = "bodyText"
    AUTHOR = "author"
    MILESTONE = "milestone"
    CLOSED_AT = "closedAt"
    REACTION_GROUPS = "reactionGroups"
    CONTENT = "content"
    USERS = "users"
    COMMENTS = "comments"
    IS_MINIMIZED = "isMinimized"
    MINIMIZED_REASON = "minimizedReason"
    CHANGED_FILES = "changedFiles"
    CLOSED = "closed"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    ADDITIONS = "additions"
    DELETIONS = "deletions"
    HEAD_REF_NAME = "headRefName"
    HEAD_REF_OID = "headRefOid"
    MERGED = "merged"
    MERGED_AT = "merged"
    MERGED_BY = "mergedBy"
    FILE_PATH = "path"


class ReleaseStatic(metaclass=BaseStatic):
    IS_PRE_RELEASE = "isPrerelease"
    DOWNLOAD_COUNT = "downloadCount"
    SIZE = "size"
    CONTENT_TYPE = "contentType"
    TAG_NAME = "tagName"
    RELEASES = "releases"
    AUTHOR = "author"
    RELEASE_ASSETS = "releaseAssets"
