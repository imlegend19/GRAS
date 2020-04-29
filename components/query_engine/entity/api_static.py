class BaseModel(type):
    def __setattr__(self, name, value):
        raise ValueError("Cannot change the value of a read-only variable.")


class APIStatic(metaclass=BaseModel):
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


class RepositoryStatic(metaclass=BaseModel):
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
    OID = "oid"
    LANGUAGES = "languages"
    SIZE = "size"


class MilestoneStatic(metaclass=BaseModel):
    MILESTONES = "milestones"
    DUE_ON = "dueOn"
    TITLE = "title"
    CLOSED_AT = "closedAt"
    STATE = "state"
    CREATOR = "creator"


class LabelStatic(metaclass=BaseModel):
    LABELS = "labels"
    COLOR = "color"


class IssueStatic(metaclass=BaseModel):
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
