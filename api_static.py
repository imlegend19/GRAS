class APIStatic:
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


class RepositoryStatic:
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


class MilestoneStatic:
    MILESTONES = "milestones"
    DUE_ON = "dueOn"
    TITLE = "title"
    CLOSED_AT = "closedAt"
    NUMBER = "number"
    STATE = "state"
    CREATOR = "creator"


class LanguageStatic:
    LANGUAGES = "languages"
    SIZE = "size"


class LabelStatic:
    LABELS = "labels"
    NAME = "name"
    ID = "id"
    COLOR = "color"


class IssueStatic:
    STATE = "state"
    REACTIONS = "reactions"
    LABELS = "labels"
    ASSIGNEES = "assignees"
    ISSUES = "issues"
    TITLE = "title"
    BODY_TEXT = "bodyText"
    AUTHOR = "author"
    NUMBER = "number"
    MILESTONE = "milestone"
    CREATED_AT = "createdAt"
