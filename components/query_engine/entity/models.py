from abc import ABCMeta, abstractmethod

from components.query_engine.entity.api_static import *
from components.utils import Utils


class BaseModel(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def object_decoder(self, dic):
        pass


class RepositoryModel(BaseModel):
    def __init__(self, created_at, updated_at, disk_usage, url, owner_login, name, description, fork_count,
                 homepage_url, is_archived, is_fork, primary_language, stargazer_count, watcher_count):
        super().__init__()

        self.name = name
        self.description = description
        self.fork_count = fork_count
        self.owner_login = owner_login
        self.url = url
        self.watcher_count = watcher_count
        self.stargazer_count = stargazer_count
        self.primary_language = primary_language
        self.is_fork = is_fork
        self.is_archived = is_archived
        self.homepage_url = homepage_url
        self.disk_usage = disk_usage
        self.updated_at = updated_at
        self.created_at = created_at

    def object_decoder(self, dic):
        obj = RepositoryModel(
            name=dic[APIStatic.NAME],
            url=dic[APIStatic.URL],
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            description=dic[APIStatic.DESCRIPTION],
            disk_usage=dic[RepositoryStatic.DISK_USAGE],
            fork_count=dic[RepositoryStatic.FORK_COUNT],
            homepage_url=dic[RepositoryStatic.HOMEPAGE_URL],
            is_archived=dic[RepositoryStatic.IS_ARCHIVED],
            is_fork=dic[RepositoryStatic.IS_FORK],
            owner_login=dic[RepositoryStatic.OWNER][APIStatic.LOGIN],
            primary_language=dic[RepositoryStatic.PRIMARY_LANGUAGE][APIStatic.NAME],
            stargazer_count=dic[RepositoryStatic.STARGAZERS][APIStatic.TOTAL_COUNT],
            watcher_count=dic[RepositoryStatic.WATCHERS][APIStatic.TOTAL_COUNT],
        )

        return obj


class MilestoneModel(BaseModel):
    def __init__(self, closed_at, created_at, creator_login, description, due_on, state, title, updated_at, number):
        super().__init__()

        self.number = number
        self.title = title
        self.state = state
        self.due_on = due_on
        self.description = description
        self.creator_login = creator_login
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at

    def object_decoder(self, dic):
        obj = MilestoneModel(
            number=dic[APIStatic.NUMBER],
            title=dic[MilestoneStatic.TITLE],
            state=dic[MilestoneStatic.STATE],
            due_on=dic[MilestoneStatic.DUE_ON],
            description=dic[APIStatic.DESCRIPTION],
            creator_login=dic[MilestoneStatic.CREATOR][APIStatic.LOGIN],
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            closed_at=dic[MilestoneStatic.CLOSED_AT],
        )

        return obj


class StargazerModel(BaseModel):
    def __init__(self, login, starred_at):
        super().__init__()

        self.login = login
        self.starred_at = starred_at

    def object_decoder(self, dic):
        obj = StargazerModel(
            starred_at=dic[RepositoryStatic.STARRED_AT],
            login=dic[APIStatic.NODE][APIStatic.LOGIN],
        )

        return obj


class LabelModel(BaseModel):
    def __init__(self, color, name, created_at):
        super().__init__()

        self.color = color
        self.name = name
        self.created_at = created_at

    def object_decoder(self, dic):
        obj = LabelModel(
            color=dic[APIStatic.NODE][LabelStatic.COLOR],
            name=dic[APIStatic.NODE][APIStatic.NAME],
            created_at=dic[APIStatic.NODE][APIStatic.CREATED_AT],
        )

        return obj


class BranchModel(BaseModel):
    def __init__(self, name, commit_id):
        super().__init__()

        self.commit_id = commit_id
        self.name = name

    def object_decoder(self, dic):
        obj = BranchModel(
            name=dic[APIStatic.NAME],
            commit_id=dic[RepositoryStatic.TARGET][RepositoryStatic.OID],
        )

        return obj


class WatcherModel(BaseModel):
    def __init__(self, login, created_at):
        super().__init__()

        self.login = login
        self.created_at = created_at

    def object_decoder(self, dic):
        obj = WatcherModel(
            login=dic[APIStatic.LOGIN],
            created_at=dic[APIStatic.CREATED_AT]
        )

        return obj


class LanguageModel(BaseModel):
    def __init__(self, language, size):
        super().__init__()

        self.language = language
        self.size = size

    def object_decoder(self, dic):
        obj = LanguageModel(
            language=dic[APIStatic.NODE][APIStatic.NAME],
            size=dic[RepositoryStatic.SIZE] / 1024,
        )

        return obj


class IssueModel(Utils, BaseModel):
    def __init__(self, created_at, updated_at, closed_at, title, body, author_login, assignees, number,
                 milestone_number, labels, state, positive_reaction_count, negative_reaction_count,
                 ambiguous_reaction_count):
        super().__init__()

        self.ambiguous_reaction_count = ambiguous_reaction_count
        self.negative_reaction_count = negative_reaction_count
        self.positive_reaction_count = positive_reaction_count
        self.closed_at = closed_at
        self.updated_at = updated_at
        self.state = state
        self.labels = labels
        self.milestone_number = milestone_number
        self.number = number
        self.assignees = assignees
        self.author_login = author_login
        self.body = body
        self.title = title
        self.created_at = created_at

    def object_decoder(self, dic):
        obj = IssueModel(
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            closed_at=dic[IssueStatic.CLOSED_AT],
            title=dic[IssueStatic.TITLE],
            body=dic[IssueStatic.BODY_TEXT],
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][APIStatic.LOGIN],
            assignees=list(node[APIStatic.LOGIN] for node in dic[IssueStatic.ASSIGNEES][APIStatic.NODES]),
            number=dic[APIStatic.NUMBER],
            milestone_number=dic[IssueStatic.MILESTONE],
            labels=list(node[APIStatic.NAME] for node in dic[IssueStatic.LABELS][APIStatic.NODES]),
            positive_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            state=dic[IssueStatic.STATE]
        )

        return obj


class IssueCommentModel(Utils, BaseModel):
    def __init__(self, author_login, body, created_at, updated_at, is_minimized, minimized_reason,
                 positive_reaction_count, negative_reaction_count, ambiguous_reaction_count):
        super().__init__()

        self.updated_at = updated_at
        self.author_login = author_login
        self.body = body
        self.created_at = created_at
        self.is_minimized = is_minimized
        self.minimized_reason = minimized_reason
        self.positive_reaction_count = positive_reaction_count
        self.negative_reaction_count = negative_reaction_count
        self.ambiguous_reaction_count = ambiguous_reaction_count

    def object_decoder(self, dic):
        obj = IssueCommentModel(
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            body=dic[IssueStatic.BODY_TEXT],
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][APIStatic.LOGIN],
            positive_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            is_minimized=dic[IssueStatic.IS_MINIMIZED],
            minimized_reason=dic[IssueStatic.MINIMIZED_REASON]
        )

        return obj


class PullRequestModel(Utils, BaseModel):
    def __init__(self, number, title, body, author_login, assignees, num_files_changed, closed, closed_at, created_at,
                 updated_at, additions, deletions, head_ref_name, head_ref_oid, labels, merged, merged_at, merged_by,
                 milestone_number, positive_reaction_count, negative_reaction_count, ambiguous_reaction_count, state):
        super().__init__()

        self.number = number
        self.title = title
        self.body = body
        self.author_login = author_login
        self.assignees = assignees
        self.num_files_changed = num_files_changed
        self.closed = closed
        self.closed_at = closed_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.additions = additions
        self.deletions = deletions
        self.head_ref_name = head_ref_name
        self.head_ref_oid = head_ref_oid
        self.labels = labels
        self.merged = merged
        self.merged_at = merged_at
        self.merged_by = merged_by
        self.milestone_number = milestone_number
        self.positive_reaction_count = positive_reaction_count
        self.negative_reaction_count = negative_reaction_count
        self.ambiguous_reaction_count = ambiguous_reaction_count
        self.state = state

    def object_decoder(self, dic):
        obj = PullRequestModel(
            number=dic[APIStatic.NUMBER],
            title=dic[IssueStatic.TITLE],
            author_login=dic[IssueStatic.AUTHOR][APIStatic.LOGIN],
            assignees=list(node[APIStatic.LOGIN] for node in dic[IssueStatic.ASSIGNEES][APIStatic.NODES]),
            body=dic[IssueStatic.BODY_TEXT],
            num_files_changed=dic[IssueStatic.CHANGED_FILES],
            closed=dic[IssueStatic.CLOSED],
            closed_at=dic[IssueStatic.CLOSED_AT],
            created_at=dic[IssueStatic.CREATED_AT],
            updated_at=dic[IssueStatic.UPDATED_AT],
            additions=dic[IssueStatic.ADDITIONS],
            deletions=dic[IssueStatic.DELETIONS],
            head_ref_name=dic[IssueStatic.HEAD_REF_NAME],
            head_ref_oid=dic[IssueStatic.HEAD_REF_OID],
            labels=list(node[APIStatic.NAME] for node in dic[IssueStatic.LABELS][APIStatic.NODES]),
            merged=dic[IssueStatic.MERGED],
            merged_at=dic[IssueStatic.MERGED_AT],
            merged_by=dic[IssueStatic.MERGED_BY][APIStatic.LOGIN] if dic[IssueStatic.MERGED_BY] is not None else None,
            milestone_number=dic[IssueStatic.MILESTONE][APIStatic.NUMBER] if
            dic[IssueStatic.MILESTONE] is not None else None,
            positive_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            state=dic[IssueStatic.STATE]
        )

        return obj
