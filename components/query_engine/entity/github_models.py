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
    def __init__(self, created_at, updated_at, disk_usage, url, name, description, fork_count,
                 homepage_url, is_archived, is_fork, primary_language, stargazer_count, watcher_count, forked_from):
        super().__init__()
        
        self.name = name
        self.description = description
        self.fork_count = fork_count
        self.url = url
        self.watcher_count = watcher_count
        self.stargazer_count = stargazer_count
        self.primary_language = primary_language
        self.is_fork = is_fork
        self.forked_from = forked_from
        self.is_archived = is_archived
        self.homepage_url = homepage_url
        self.disk_usage = disk_usage
        self.updated_at = updated_at
        self.created_at = created_at
    
    def object_decoder(self, dic):
        obj = RepositoryModel(
            name=dic[UserStatic.NAME],
            url=dic[APIStaticV4.URL],
            created_at=dic[APIStaticV4.CREATED_AT],
            updated_at=dic[APIStaticV4.UPDATED_AT],
            description=dic[APIStaticV4.DESCRIPTION],
            disk_usage=dic[RepositoryStatic.DISK_USAGE],
            fork_count=dic[RepositoryStatic.FORK_COUNT],
            homepage_url=dic[RepositoryStatic.HOMEPAGE_URL],
            is_archived=dic[RepositoryStatic.IS_ARCHIVED],
            is_fork=dic[RepositoryStatic.IS_FORK],
            forked_from=dic[RepositoryStatic.PARENT][
                APIStaticV4.URL] if dic[RepositoryStatic.PARENT] is not None else None,
            primary_language=dic[RepositoryStatic.PRIMARY_LANGUAGE][UserStatic.NAME],
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
            creator_login=dic[MilestoneStatic.CREATOR][UserStatic.LOGIN],
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
            login=dic[APIStaticV4.NODE][UserStatic.LOGIN],
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
            name=dic[APIStaticV4.NODE][UserStatic.NAME],
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
            name=dic[UserStatic.NAME],
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
            login=dic[UserStatic.LOGIN],
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
            language=dic[APIStaticV4.NODE][UserStatic.NAME],
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
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][UserStatic.LOGIN],
            assignees=list(node[UserStatic.LOGIN] for node in dic[IssueStatic.ASSIGNEES][APIStaticV4.NODES]),
            number=dic[APIStaticV4.NUMBER],
            milestone_number=dic[IssueStatic.MILESTONE],
            labels=list(node[UserStatic.NAME] for node in dic[IssueStatic.LABELS][APIStaticV4.NODES]),
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
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][UserStatic.LOGIN],
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
            author_login=dic[IssueStatic.AUTHOR][UserStatic.LOGIN],
            assignees=list(node[UserStatic.LOGIN] for node in (dic[IssueStatic.ASSIGNEES][APIStaticV4.NODES]
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
            labels=list(node[UserStatic.NAME] for node in dic[IssueStatic.LABELS][APIStaticV4.NODES]),
            merged=dic[IssueStatic.MERGED],
            merged_at=dic[IssueStatic.MERGED_AT],
            merged_by=dic[IssueStatic.MERGED_BY][UserStatic.LOGIN] if dic[IssueStatic.MERGED_BY] is not None else None,
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
            name=dic[UserStatic.NAME],
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
                UserStatic.LOGIN] if dic[ReleaseStatic.AUTHOR] is not None else None,
            description=dic[APIStaticV4.DESCRIPTION],
            created_at=dic[APIStaticV4.CREATED_AT],
            isPrerelease=dic[ReleaseStatic.IS_PRE_RELEASE],
            name=dic[UserStatic.NAME],
            release_assets=list(AssetModel.object_decoder(node) for node in
                                dic[ReleaseStatic.RELEASE_ASSETS][APIStaticV4.NODES]),
            tag_name=dic[ReleaseStatic.TAG_NAME],
            updated_at=dic[APIStaticV4.UPDATED_AT],
        )
        
        return obj


class CommitModelV3(BaseModel):
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
        obj = CommitModelV3(
            commit_id=dic[CommitStatic.SHA],
            author_name=dic[CommitStatic.COMMIT][CommitStatic.AUTHOR][
                APIStaticV3.NAME] if dic[CommitStatic.COMMIT][CommitStatic.AUTHOR] is not None else None,
            author_email=dic[CommitStatic.COMMIT][CommitStatic.AUTHOR][
                APIStaticV3.EMAIL] if dic[CommitStatic.COMMIT][CommitStatic.AUTHOR] is not None else None,
            authored_date=dic[CommitStatic.COMMIT][CommitStatic.AUTHOR][
                APIStaticV3.DATE] if dic[CommitStatic.COMMIT][CommitStatic.AUTHOR] is not None else None,
            author_login=dic[CommitStatic.AUTHOR][
                APIStaticV3.LOGIN] if dic[CommitStatic.AUTHOR] is not None else None,
            committed_date=dic[CommitStatic.COMMIT][CommitStatic.COMMITTER][
                APIStaticV3.DATE] if dic[CommitStatic.COMMIT][CommitStatic.COMMITTER] is not None else None,
            committer_email=dic[CommitStatic.COMMIT][CommitStatic.COMMITTER][
                APIStaticV3.EMAIL] if dic[CommitStatic.COMMIT][CommitStatic.COMMITTER] is not None else None,
            committer_name=dic[CommitStatic.COMMIT][CommitStatic.COMMITTER][
                APIStaticV3.NAME] if dic[CommitStatic.COMMIT][CommitStatic.COMMITTER] is not None else None,
            committer_login=dic[CommitStatic.COMMITTER][
                APIStaticV3.LOGIN] if dic[CommitStatic.COMMITTER] is not None else None,
            msg=dic[CommitStatic.COMMIT][CommitStatic.MESSAGE],
            is_merge=merge
        )
        
        return obj


class CommitModelV4(BaseModel):
    def __init__(self, commit_id, additions, deletions, author_name, author_email, author_login, authored_date,
                 committer_name, committer_email, committer_login, committed_date, message, state, num_changed_files,
                 is_merge):
        super().__init__()
        
        self.commit_id = commit_id
        self.additions = additions
        self.deletions = deletions
        self.author_name = author_name
        self.author_email = author_email
        self.author_login = author_login
        self.authored_date = authored_date
        self.committer_name = committer_name
        self.committer_email = committer_email
        self.committer_login = committer_login
        self.committed_date = committed_date
        self.message = message
        self.state = state
        self.num_changed_files = num_changed_files
        self.is_merge = is_merge
    
    def object_decoder(self, dic):
        obj = CommitModelV4(
            commit_id=dic[APIStaticV4.OID],
            additions=dic[CommitStatic.ADDITIONS],
            deletions=dic[CommitStatic.DELETIONS],
            author_name=dic[CommitStatic.AUTHOR][UserStatic.NAME],
            author_email=dic[CommitStatic.AUTHOR][UserStatic.EMAIL],
            author_login=dic[CommitStatic.AUTHOR][UserStatic.USER][
                UserStatic.LOGIN] if dic[CommitStatic.AUTHOR][UserStatic.USER] is not None else None,
            authored_date=dic[CommitStatic.AUTHORED_DATE],
            committer_name=dic[CommitStatic.COMMITTER][UserStatic.NAME],
            committer_email=dic[CommitStatic.COMMITTER][UserStatic.EMAIL],
            committer_login=dic[CommitStatic.COMMITTER][UserStatic.USER][
                UserStatic.LOGIN] if dic[CommitStatic.COMMITTER][UserStatic.USER] is not None else None,
            committed_date=dic[CommitStatic.COMMITTED_DATE],
            message=dic[CommitStatic.MESSAGE],
            state=dic[CommitStatic.STATUS][CommitStatic.STATE] if dic[CommitStatic.STATUS] is not None else None,
            num_changed_files=dic[CommitStatic.CHANGED_FILES],
            is_merge=True if dic[CommitStatic.PARENTS][APIStaticV4.TOTAL_COUNT] > 1 else False
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
            filename=dic[CommitStatic.FILENAME],
            status=dic[CommitStatic.STATUS],
            additions=dic[CommitStatic.ADDITIONS],
            deletions=dic[CommitStatic.DELETIONS],
            changes=dic[CommitStatic.CHANGES],
            patch=dic[CommitStatic.PATCH]
        )
        
        return obj


class UserModel(BaseModel):
    def __init__(self, login, name, email, created_at, total_followers, location, updated_at):
        super().__init__()
        
        self.login = login
        self.name = name
        self.email = email
        self.created_at = created_at
        self.total_followers = total_followers
        self.location = location
        self.updated_at = updated_at
    
    def object_decoder(self, dic):
        obj = UserModel(
            login=dic[UserStatic.LOGIN],
            name=dic[UserStatic.NAME],
            email=dic[UserStatic.EMAIL],
            created_at=dic[APIStaticV4.CREATED_AT],
            total_followers=dic[UserStatic.FOLLOWERS][APIStaticV4.TOTAL_COUNT],
            location=dic[UserStatic.LOCATION],
            updated_at=dic[APIStaticV4.UPDATED_AT]
        )
        
        return obj


class TopicModel(BaseModel):
    def __init__(self, url, topic_name, stargazer_count):
        super().__init__()
        
        self.url = url
        self.topic_name = topic_name
        self.stargazer_count = stargazer_count
    
    def object_decoder(self, dic):
        obj = TopicModel(
            url=dic[APIStaticV4.URL],
            topic_name=dic[RepositoryStatic.TOPIC][UserStatic.NAME],
            stargazer_count=dic[RepositoryStatic.TOPIC][RepositoryStatic.STARGAZERS][APIStaticV4.TOTAL_COUNT]
        )
        
        return obj


class CommitCommentModel(BaseModel):
    def __init__(self, author_login, body, commit_id, created_at, path, position, positive_reaction_count,
                 negative_reaction_count, ambiguous_reaction_count, updated_at):
        super().__init__()
        
        self.author_login = author_login
        self.body = body
        self.commit_id = commit_id
        self.created_at = created_at
        self.path = path
        self.position = position
        self.positive_reaction_count = positive_reaction_count
        self.negative_reaction_count = negative_reaction_count
        self.ambiguous_reaction_count = ambiguous_reaction_count
        self.updated_at = updated_at
    
    def object_decoder(self, dic):
        if dic[CommitStatic.COMMIT] is None:
            return None
        
        obj = CommitCommentModel(
            author_login=dic[CommitStatic.AUTHOR][UserStatic.LOGIN],
            body=dic[CommitStatic.BODY_TEXT],
            commit_id=dic[CommitStatic.COMMIT][APIStaticV4.OID],
            created_at=dic[APIStaticV4.CREATED_AT],
            updated_at=dic[APIStaticV4.UPDATED_AT],
            path=dic[CommitStatic.PATH],
            position=dic[CommitStatic.POSITION],
            positive_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            ambiguous_reaction_count=reaction_count(dic[IssueStatic.REACTION_GROUPS], -1)
        )
        
        return obj


class ForkModel(BaseModel):
    def __init__(self, login, created_at):
        super().__init__()
        
        self.login = login
        self.created_at = created_at
    
    def object_decoder(self, dic):
        obj = ForkModel(
            login=dic[RepositoryStatic.OWNER][UserStatic.LOGIN],
            created_at=dic[APIStaticV4.CREATED_AT]
        )
        return obj


class IssueEventModel(BaseModel):
    def __init__(self, number, who, when, event_type, added, added_type, removed, removed_type, is_cross_repository):
        super().__init__()
        
        self.number = number
        self.who = who
        self.when = when
        self.event_type = event_type
        self.added = added
        self.added_type = added_type
        self.removed = removed
        self.removed_type = removed_type
        self.is_cross_repository = is_cross_repository
    
    def object_decoder(self, dic, number):
        event_type = dic[IssueEventStatic.EVENT_TYPE]
        obj = IssueEventModel(
            number=number,
            event_type=event_type,
            who=None if dic[IssueEventStatic.WHO] is None else dic[IssueEventStatic.WHO][UserStatic.LOGIN],
            when=dic[IssueEventStatic.WHEN],
            added=None,
            added_type=None,
            removed=None,
            removed_type=None,
            is_cross_repository=False
        )
        
        if event_type == IssueEventStatic.ASSIGNED_EVENT:
            obj.added = dic[IssueEventStatic.ADDED][UserStatic.LOGIN]
            obj.added_type = "USER"
        elif event_type == IssueEventStatic.CROSS_REFERENCED_EVENT:
            obj.added = dic[IssueEventStatic.ADDED][APIStaticV4.NUMBER]
            obj.added_type = dic[IssueEventStatic.ADDED][IssueEventStatic.TYPE].upper()
            obj.is_cross_repository = True
        elif event_type == IssueEventStatic.DEMILESTONED_EVENT:
            obj.removed = dic[IssueEventStatic.ADDED]
            obj.removed_type = "MILESTONE"
        elif event_type == IssueEventStatic.LABELED_EVENT:
            obj.added = dic[IssueEventStatic.ADDED][UserStatic.NAME]
            obj.added_type = "LABEL"
        elif event_type == IssueEventStatic.MARKED_AS_DUPLICATE_EVENT:
            pass
        elif event_type == IssueEventStatic.MENTIONED_EVENT:
            pass
        elif event_type == IssueEventStatic.MILESTONED_EVENT:
            obj.added = dic[IssueEventStatic.ADDED]
            obj.added_type = "MILESTONE"
        elif event_type == IssueEventStatic.PINNED_EVENT:
            pass
        elif event_type == IssueEventStatic.REFERENCED_EVENT:
            obj.added = dic[IssueEventStatic.ADDED][APIStaticV4.OID]
            obj.added_type = "COMMIT_ID"
            obj.is_cross_repository = True
        elif event_type == IssueEventStatic.RENAMED_TITLE_EVENT:
            obj.removed = dic[IssueEventStatic.REMOVED]
            obj.removed_type = "TITLE"
            obj.added = dic[IssueEventStatic.ADDED]
            obj.added_type = "TITLE"
        elif event_type == IssueEventStatic.REOPENED_EVENT:
            pass
        elif event_type == IssueEventStatic.TRANSFERRED_EVENT:
            rem = dic[IssueEventStatic.REMOVED]
            obj.removed = rem[RepositoryStatic.OWNER] + "/" + rem[UserStatic.NAME]
            obj.removed_type = "REPOSITORY"
        elif event_type == IssueEventStatic.UNASSIGNED_EVENT:
            pass
        elif event_type == IssueEventStatic.UNLABELED_EVENT:
            obj.removed = dic[IssueEventStatic.REMOVED][UserStatic.NAME]
            obj.removed_type = "LABEL"
        elif event_type == IssueEventStatic.UNMARKED_AS_DUPLICATE_EVENT:
            pass
        elif event_type == IssueEventStatic.UNPINNED_EVENT:
            pass
        else:
            raise NotImplementedError
        
        return obj
