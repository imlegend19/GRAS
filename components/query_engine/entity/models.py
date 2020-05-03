from abc import ABCMeta, abstractmethod

from components.query_engine.entity.api_static import *
from components.utils import *


class BaseModel(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def object_decoder(self, **kwargs):
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
            name=dic[APIStaticV4.NAME],
            url=dic[APIStaticV4.URL],
            created_at=dic[APIStaticV4.CREATED_AT],
            updated_at=dic[APIStaticV4.UPDATED_AT],
            description=dic[APIStaticV4.DESCRIPTION],
            disk_usage=dic[RepositoryStatic.DISK_USAGE],
            fork_count=dic[RepositoryStatic.FORK_COUNT],
            homepage_url=dic[RepositoryStatic.HOMEPAGE_URL],
            is_archived=dic[RepositoryStatic.IS_ARCHIVED],
            is_fork=dic[RepositoryStatic.IS_FORK],
            owner_login=dic[RepositoryStatic.OWNER][APIStaticV4.LOGIN],
            primary_language=dic[RepositoryStatic.PRIMARY_LANGUAGE][APIStaticV4.NAME],
            stargazer_count=dic[RepositoryStatic.STARGAZERS][APIStaticV4.TOTAL_COUNT],
            watcher_count=dic[RepositoryStatic.WATCHERS][APIStaticV4.TOTAL_COUNT],
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
            number=dic[APIStaticV4.NUMBER],
            title=dic[MilestoneStatic.TITLE],
            state=dic[MilestoneStatic.STATE],
            due_on=dic[MilestoneStatic.DUE_ON],
            description=dic[APIStaticV4.DESCRIPTION],
            creator_login=dic[MilestoneStatic.CREATOR][APIStaticV4.LOGIN],
            created_at=dic[APIStaticV4.CREATED_AT],
            updated_at=dic[APIStaticV4.UPDATED_AT],
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
            login=dic[APIStaticV4.NODE][APIStaticV4.LOGIN],
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
            color=dic[APIStaticV4.NODE][LabelStatic.COLOR],
            name=dic[APIStaticV4.NODE][APIStaticV4.NAME],
            created_at=dic[APIStaticV4.NODE][APIStaticV4.CREATED_AT],
        )

        return obj


class BranchModel(BaseModel):
    def __init__(self, name, commit_id):
        super().__init__()

        self.commit_id = commit_id
        self.name = name

    def object_decoder(self, dic):
        obj = BranchModel(
            name=dic[APIStaticV4.NAME],
            commit_id=dic[RepositoryStatic.TARGET][APIStaticV4.OID],
        )

        return obj


class WatcherModel(BaseModel):
    def __init__(self, login, created_at):
        super().__init__()

        self.login = login
        self.created_at = created_at

    def object_decoder(self, dic):
        obj = WatcherModel(
            login=dic[APIStaticV4.LOGIN],
            created_at=dic[APIStaticV4.CREATED_AT]
        )

        return obj


class LanguageModel(BaseModel):
    def __init__(self, language, size):
        super().__init__()

        self.language = language
        self.size = size

    def object_decoder(self, dic):
        obj = LanguageModel(
            language=dic[APIStaticV4.NODE][APIStaticV4.NAME],
            size=dic[RepositoryStatic.SIZE] / 1024,
        )

        return obj


class IssueModel(BaseModel):
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
            created_at=dic[APIStaticV4.CREATED_AT],
            updated_at=dic[APIStaticV4.UPDATED_AT],
            closed_at=dic[IssueStatic.CLOSED_AT],
            title=dic[IssueStatic.TITLE],
            body=dic[IssueStatic.BODY_TEXT],
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][APIStaticV4.LOGIN],
            assignees=list(node[APIStaticV4.LOGIN] for node in dic[IssueStatic.ASSIGNEES][APIStaticV4.NODES]),
            number=dic[APIStaticV4.NUMBER],
            milestone_number=dic[IssueStatic.MILESTONE],
            labels=list(node[APIStaticV4.NAME] for node in dic[IssueStatic.LABELS][APIStaticV4.NODES]),
            positive_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            state=dic[IssueStatic.STATE]
        )

        return obj


class IssueCommentModel(BaseModel):
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
            created_at=dic[APIStaticV4.CREATED_AT],
            updated_at=dic[APIStaticV4.UPDATED_AT],
            body=dic[IssueStatic.BODY_TEXT],
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][APIStaticV4.LOGIN],
            positive_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            is_minimized=dic[IssueStatic.IS_MINIMIZED],
            minimized_reason=dic[IssueStatic.MINIMIZED_REASON]
        )

        return obj


class FileModel(BaseModel):
    def __init__(self, path, additions, deletions):
        super().__init__()

        self.path = path
        self.additions = additions
        self.deletions = deletions

    def object_decoder(self, dic):
        obj = FileModel(
            path=dic[IssueStatic.FILE_PATH],
            additions=dic[IssueStatic.ADDITIONS],
            deletions=dic[IssueStatic.DELETIONS]
        )

        return obj


class PullRequestModel(BaseModel):
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
            number=dic[APIStaticV4.NUMBER],
            title=dic[IssueStatic.TITLE],
            author_login=dic[IssueStatic.AUTHOR][APIStaticV4.LOGIN],
            assignees=list(node[APIStaticV4.LOGIN] for node in (dic[IssueStatic.ASSIGNEES][APIStaticV4.NODES]
                                                                if dic[IssueStatic.ASSIGNEES] is not None else [])),
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
            labels=list(node[APIStaticV4.NAME] for node in dic[IssueStatic.LABELS][APIStaticV4.NODES]),
            merged=dic[IssueStatic.MERGED],
            merged_at=dic[IssueStatic.MERGED_AT],
            merged_by=dic[IssueStatic.MERGED_BY][APIStaticV4.LOGIN] if dic[IssueStatic.MERGED_BY] is not None else None,
            milestone_number=dic[IssueStatic.MILESTONE][APIStaticV4.NUMBER] if
            dic[IssueStatic.MILESTONE] is not None else None,
            positive_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            state=dic[IssueStatic.STATE]
        )

        return obj


class AssetModel(BaseModel):
    def __init__(self, download_count, name, size, updated_at, content_type, created_at):
        super().__init__()

        self.download_count = download_count
        self.name = name
        self.size = size
        self.updated_at = updated_at
        self.content_type = content_type
        self.created_at = created_at

    @staticmethod
    def object_decoder(dic, **kwargs):
        obj = AssetModel(
            download_count=dic[ReleaseStatic.DOWNLOAD_COUNT],
            name=dic[APIStaticV4.NAME],
            size=dic[ReleaseStatic.SIZE],
            updated_at=dic[APIStaticV4.UPDATED_AT],
            content_type=dic[ReleaseStatic.CONTENT_TYPE],
            created_at=dic[APIStaticV4.CREATED_AT],
        )

        return obj


class ReleaseModel(BaseModel):
    def __init__(self, author_login, description, created_at, isPrerelease, name, release_assets, tag_name, updated_at):
        super().__init__()

        self.author_login = author_login
        self.description = description
        self.created_at = created_at
        self.isPrerelease = isPrerelease
        self.name = name
        self.release_assets = release_assets
        self.tag_name = tag_name
        self.updated_at = updated_at

    def object_decoder(self, dic):
        obj = ReleaseModel(
            author_login=dic[ReleaseStatic.AUTHOR][
                APIStaticV4.LOGIN] if dic[ReleaseStatic.AUTHOR] is not None else None,
            description=dic[APIStaticV4.DESCRIPTION],
            created_at=dic[APIStaticV4.CREATED_AT],
            isPrerelease=dic[ReleaseStatic.IS_PRE_RELEASE],
            name=dic[APIStaticV4.NAME],
            release_assets=list(AssetModel.object_decoder(node) for node in
                                dic[ReleaseStatic.RELEASE_ASSETS][APIStaticV4.NODES]),
            tag_name=dic[ReleaseStatic.TAG_NAME],
            updated_at=dic[APIStaticV4.UPDATED_AT],
        )

        return obj


class CommitModel(BaseModel):
    def __init__(self, commit_id, author_login, author_name, author_email, authored_date, committed_date,
                 committer_name, committer_email, committer_login, msg, is_merge):
        super().__init__()

        self.commit_id = commit_id
        self.author_name = author_name
        self.author_email = author_email
        self.author_login = author_login
        self.authored_date = authored_date
        self.committed_date = committed_date
        self.committer_name = committer_name
        self.committer_email = committer_email
        self.committer_login = committer_login
        self.msg = msg
        self.is_merge = is_merge

    def object_decoder(self, dic, merge):
        obj = CommitModel(
            commit_id=dic[CommitStaticV3.SHA],
            author_name=dic[CommitStaticV3.COMMIT][CommitStaticV3.AUTHOR][
                APIStaticV3.NAME] if dic[CommitStaticV3.COMMIT][CommitStaticV3.AUTHOR] is not None else None,
            author_email=dic[CommitStaticV3.COMMIT][CommitStaticV3.AUTHOR][
                APIStaticV3.EMAIL] if dic[CommitStaticV3.COMMIT][CommitStaticV3.AUTHOR] is not None else None,
            authored_date=dic[CommitStaticV3.COMMIT][CommitStaticV3.AUTHOR][
                APIStaticV3.DATE] if dic[CommitStaticV3.COMMIT][CommitStaticV3.AUTHOR] is not None else None,
            author_login=dic[CommitStaticV3.AUTHOR][
                APIStaticV3.LOGIN] if dic[CommitStaticV3.AUTHOR] is not None else None,
            committed_date=dic[CommitStaticV3.COMMIT][CommitStaticV3.COMMITTER][
                APIStaticV3.DATE] if dic[CommitStaticV3.COMMIT][CommitStaticV3.COMMITTER] is not None else None,
            committer_email=dic[CommitStaticV3.COMMIT][CommitStaticV3.COMMITTER][
                APIStaticV3.EMAIL] if dic[CommitStaticV3.COMMIT][CommitStaticV3.COMMITTER] is not None else None,
            committer_name=dic[CommitStaticV3.COMMIT][CommitStaticV3.COMMITTER][
                APIStaticV3.NAME] if dic[CommitStaticV3.COMMIT][CommitStaticV3.COMMITTER] is not None else None,
            committer_login=dic[CommitStaticV3.COMMITTER][
                APIStaticV3.LOGIN] if dic[CommitStaticV3.COMMITTER] is not None else None,
            msg=dic[CommitStaticV3.COMMIT][CommitStaticV3.MESSAGE],
            is_merge=merge
        )

        return obj


class CodeChangeModel(BaseModel):
    def __init__(self, filename, status, additions, deletions, changes, patch):
        super().__init__()

        self.filename = filename
        self.status = status
        self.additions = additions
        self.deletions = deletions
        self.changes = changes
        self.patch = patch

    def object_decoder(self, dic):
        obj = CodeChangeModel(
            filename=dic[CommitStaticV3.FILENAME],
            status=dic[CommitStaticV3.STATUS],
            additions=dic[CommitStaticV3.ADDITIONS],
            deletions=dic[CommitStaticV3.DELETIONS],
            changes=dic[CommitStaticV3.CHANGES],
            patch=dic[CommitStaticV3.PATCH]
        )

        return obj
