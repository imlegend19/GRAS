import enum

from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.schema import CheckConstraint, Column, ForeignKey, MetaData, Table, UniqueConstraint
from sqlalchemy.types import BOOLEAN, DATETIME, INTEGER, TEXT, VARCHAR

from gras.utils import get_value, to_datetime


class State(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class LabelType(enum.Enum):
    GENERAL = "GENERAL"
    PRIORITY = "PRIORITY"
    SEVERITY = "SEVERITY"
    COMPONENT = "COMPONENT"


class EventType(enum.Enum):
    ASSIGNED_EVENT = "ASSIGNED_EVENT"
    CROSS_REFERENCED_EVENT = "CROSS_REFERENCED_EVENT"
    DEMILESTONED_EVENT = "DEMILESTONED_EVENT"
    LABELED_EVENT = "LABELED_EVENT"
    MARKED_AS_DUPLICATE_EVENT = "MARKED_AS_DUPLICATE_EVENT"
    MENTIONED_EVENT = "MENTIONED_EVENT"
    MILESTONED_EVENT = "MILESTONED_EVENT"
    PINNED_EVENT = "PINNED_EVENT"
    REFERENCED_EVENT = "REFERENCED_EVENT"
    RENAMED_TITLE_EVENT = "RENAMED_TITLE_EVENT"
    REOPENED_EVENT = "REOPENED_EVENT"
    TRANSFERRED_EVENT = "TRANSFERRED_EVENT"
    UNASSIGNED_EVENT = "UNASSIGNED_EVENT"
    UNLABELED_EVENT = "UNLABELED_EVENT"
    UNMARKED_AS_DUPLICATE_EVENT = "UNMARKED_AS_DUPLICATE_EVENT"
    UNPINNED_EVENT = "UNPINNED_EVENT"


class AddedOrRemovedType(enum.Enum):
    USER = "USER"
    MILESTONE = "MILESTONE"
    LABEL = "LABEL"
    COMMIT_ID = "COMMIT_ID"
    TITLE = "TITLE"
    REPOSITORY = "REPOSITORY"
    ISSUE = "ISSUE"
    PULL_REQUEST = "PULL_REQUEST"


class DBSchema:
    def __init__(self, conn, engine):
        self.engine = engine
        self.conn = conn
        self._metadata = MetaData()
        
        self._state_enum = self.__get_enum(State)
        self._label_enum = self.__get_enum(LabelType)
        self._event_type_enum = self.__get_enum(EventType)
        self._added_or_removed_type = self.__get_enum(AddedOrRemovedType)
    
    def __get_enum(self, cls):
        if self.engine.name == "mysql":
            return ENUM(cls), False
        elif self.engine.name == "sqlite":
            return VARCHAR(255), True
        else:
            return ENUM(cls), False
    
    @staticmethod
    def _get_string(cls):
        return ", ".join(["\'" + x + "\'" for x in cls.__members__.keys()])
    
    def create_tables(self):
        self._create_contributors_table()
        self._create_repository_table()
        self._create_repository_stats_tables()
        self._create_issues_table()
        self._create_issue_tracker_tables()
    
    def _create_contributors_table(self):
        """
        CREATE TABLE contributors (
            contributor_id INTEGER NOT NULL,
            login VARCHAR(255),
            name VARCHAR(255),
            email VARCHAR(255),
            created_at DATETIME,
            updated_at DATETIME,
            total_followers INTEGER NOT NULL,
            location VARCHAR(255),
            is_anonymous BOOLEAN NOT NULL,
            
            PRIMARY KEY (contributor_id),
            CONSTRAINT login_email_ind UNIQUE (login, email),
            CHECK (is_anonymous IN (0, 1)),
            CHECK (is_assignee IN (0, 1))
        )
        """
        self.contributors = Table(
            'contributors', self._metadata,
            Column('contributor_id', INTEGER, autoincrement=True, primary_key=True),
            Column('login', VARCHAR(255)),
            Column('name', VARCHAR(255)),
            Column('email', VARCHAR(255)),
            Column('created_at', DATETIME),
            Column('updated_at', DATETIME),
            Column('total_followers', INTEGER, nullable=False, default=0),
            Column('location', VARCHAR(255)),
            Column('is_anonymous', BOOLEAN, nullable=False, default=0),
            UniqueConstraint('login', 'email', name='login_email_ind')
        )
        
        self.contributors.create(bind=self.conn, checkfirst=True)
    
    def _create_repository_table(self):
        """
        CREATE TABLE repository (
            repo_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            owner VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            description TEXT,
            disk_usage INTEGER NOT NULL,
            fork_count INTEGER NOT NULL,
            url VARCHAR(255) NOT NULL,
            homepage_url VARCHAR(255) NOT NULL,
            primary_language VARCHAR(255) NOT NULL,
            total_stargazers INTEGER NOT NULL,
            total_watchers INTEGER NOT NULL,
            forked_from VARCHAR(255),
            
            PRIMARY KEY (repo_id)
        )
        """
        self.repository = Table(
            'repository', self._metadata,
            Column('repo_id', INTEGER, autoincrement=True, primary_key=True),
            Column('name', VARCHAR(255), nullable=False),
            Column('owner', VARCHAR(255), nullable=False),
            Column('created_at', DATETIME, nullable=False),
            Column('updated_at', DATETIME, nullable=False),
            Column('description', TEXT),
            Column('disk_usage', INTEGER, nullable=False),
            Column('fork_count', INTEGER, default=0, nullable=False),
            Column('url', VARCHAR(255), nullable=False),
            Column('homepage_url', VARCHAR(255), nullable=False),
            Column('primary_language', VARCHAR(255), nullable=False),
            Column('total_stargazers', INTEGER, default=0, nullable=False),
            Column('total_watchers', INTEGER, default=0, nullable=False),
            Column('forked_from', VARCHAR(255))
        )
    
        self.repository.create(bind=self.conn, checkfirst=True)
    
    def _create_repository_stats_tables(self):
        """
        CREATE TABLE languages (
            repo_id INTEGER,
            name VARCHAR(255) NOT NULL,
            size INTEGER NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE
        )
        
        CREATE TABLE milestones (
            id INTEGER NOT NULL,
            number INTEGER,
            repo_id INTEGER,
            creator_id INTEGER,
            title TEXT,
            description TEXT,
            due_on DATETIME,
            closed_at DATETIME,
            created_at DATETIME NOT NULL,
            updated_at DATETIME,
            state VARCHAR(255) NOT NULL,
            
            PRIMARY KEY (id),
            CONSTRAINT num_repo_ind UNIQUE (number, repo_id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(creator_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE,
            CONSTRAINT enum_check CHECK (milestones.state IN ('OPEN', 'CLOSED'))
        )
        
        CREATE TABLE stargazers (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            user_id INTEGER,
            starred_at DATETIME,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE watchers (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            user_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE topics (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            url VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            total_stargazers INTEGER NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE
        )
        
        CREATE TABLE releases (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            creator_id INTEGER,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_prerelease BOOLEAN,
            tag VARCHAR(255),
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(creator_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE forks (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            user_id INTEGER,
            forked_at DATETIME NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE branches (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            name VARCHAR(255) NOT NULL,
            target_commit_id VARCHAR(255) NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE
        )
        
        CREATE TABLE labels (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            name VARCHAR(255) NOT NULL,
            color VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            type VARCHAR(255),
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            CONSTRAINT enum_check CHECK (type IN ('GENERAL', 'PRIORITY', 'SEVERITY', 'COMPONENT'))
        )
        """
        self.languages = Table(
            'languages', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('name', VARCHAR(255), nullable=False),
            Column('size', INTEGER, default=0, nullable=False)
        )
    
        self.milestones = Table(
            'milestones', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('number', INTEGER),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('creator_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('title', TEXT),
            Column('description', TEXT),
            Column('due_on', DATETIME),
            Column('closed_at', DATETIME),
            Column('created_at', DATETIME, nullable=False),
            Column('updated_at', DATETIME),
            Column('state', self._state_enum[0], nullable=False),
            UniqueConstraint('number', 'repo_id', name='num_repo_ind')
        )
    
        if self._state_enum[1]:
            self.milestones.append_constraint(CheckConstraint(f"state IN ({self._get_string(State)})",
                                                              name='enum_check'))
    
        self.stargazers = Table(
            'stargazers', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('user_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('starred_at', DATETIME)
        )
    
        self.watchers = Table(
            'watchers', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('user_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE"))
        )
    
        self.topics = Table(
            'topics', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('url', VARCHAR(255), nullable=False),
            Column('name', VARCHAR(255), nullable=False),
            Column('total_stargazers', INTEGER, default=0, nullable=False)
        )
    
        self.releases = Table(
            'releases', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('creator_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('name', VARCHAR(255), nullable=False),
            Column('description', TEXT),
            Column('created_at', DATETIME, nullable=False),
            Column('updated_at', DATETIME, nullable=False),
            Column('is_prerelease', BOOLEAN, default=0, nullable=False),
            Column('tag', VARCHAR(255))
        )
    
        self.forks = Table(
            'forks', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('user_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('forked_at', DATETIME, nullable=False),
        )
    
        self.branches = Table(
            'branches', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('name', VARCHAR(255), nullable=False),
            Column('target_commit_id', VARCHAR(255), nullable=False)
        )
    
        self.labels = Table(
            'labels', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('name', VARCHAR(255), nullable=False),
            Column('color', VARCHAR(255), nullable=False),
            Column('created_at', DATETIME, nullable=False),
            Column('type', self._label_enum[0], default="COMPONENT")
        )
    
        if self._label_enum[1]:
            self.labels.append_constraint(CheckConstraint(f"type IN ({self._get_string(LabelType)})",
                                                          name='enum_check'))
    
        self.languages.create(bind=self.conn, checkfirst=True)
        self.milestones.create(bind=self.conn, checkfirst=True)
        self.stargazers.create(bind=self.conn, checkfirst=True)
        self.watchers.create(bind=self.conn, checkfirst=True)
        self.topics.create(bind=self.conn, checkfirst=True)
        self.releases.create(bind=self.conn, checkfirst=True)
        self.forks.create(bind=self.conn, checkfirst=True)
        self.branches.create(bind=self.conn, checkfirst=True)
        self.labels.create(bind=self.conn, checkfirst=True)

    def _create_issues_table(self):
        """
        CREATE TABLE issues (
            id INTEGER NOT NULL,
            number INTEGER,
            repo_id INTEGER,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            closed_at DATETIME,
            title TEXT,
            body TEXT,
            reporter_id INTEGER,
            milestone_id INTEGER,
            positive_reaction_count INTEGER NOT NULL,
            negative_reaction_count INTEGER NOT NULL,
            ambiguous_reaction_count INTEGER NOT NULL,
            state VARCHAR(255) NOT NULL,
            
            PRIMARY KEY (id),
            CONSTRAINT num_repo_ind UNIQUE (number, repo_id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(reporter_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE,
            FOREIGN KEY(milestone_id) REFERENCES milestones (id) ON DELETE CASCADE,
            CONSTRAINT enum_check CHECK (state IN ('OPEN', 'CLOSED'))
        )
        """
        self.issues = Table(
            'issues', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('number', INTEGER),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('created_at', DATETIME, nullable=False),
            Column('updated_at', DATETIME, nullable=False),
            Column('closed_at', DATETIME),
            Column('title', TEXT),
            Column('body', TEXT),
            Column('reporter_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('milestone_id', None, ForeignKey('milestones.id', ondelete="CASCADE")),
            Column('positive_reaction_count', INTEGER, default=0, nullable=False),
            Column('negative_reaction_count', INTEGER, default=0, nullable=False),
            Column('ambiguous_reaction_count', INTEGER, default=0, nullable=False),
            Column('state', self._state_enum[0], nullable=False),
            UniqueConstraint('number', 'repo_id', name='num_repo_ind')
        )
    
        if self._state_enum[1]:
            self.issues.append_constraint(CheckConstraint(f"state IN ({self._get_string(State)})",
                                                          name='enum_check'))
    
        self.issues.create(bind=self.conn, checkfirst=True)
    
    def _create_issue_tracker_tables(self):
        """
        CREATE TABLE issue_assignees (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            assignee_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(assignee_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE issue_labels (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            label_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(label_id) REFERENCES labels (id) ON DELETE CASCADE
        )
        
        CREATE TABLE issue_comments (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            commenter_id INTEGER,
            body TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_minimized BOOLEAN,
            minimized_reason VARCHAR(255),
            positive_reaction_count INTEGER NOT NULL,
            negative_reaction_count INTEGER NOT NULL,
            ambiguous_reaction_count INTEGER NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(commenter_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE issue_events (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            event_type VARCHAR(255) NOT NULL,
            who INTEGER,
            "when" DATETIME NOT NULL,
            added VARCHAR(255),
            added_type VARCHAR(255),
            removed VARCHAR(255),
            removed_type VARCHAR(255),
            is_cross_repository BOOLEAN NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(who) REFERENCES contributors (contributor_id) ON DELETE CASCADE,
            CHECK (is_cross_repository IN (0, 1)),
            CONSTRAINT event_enum_check CHECK (event_type IN ('ASSIGNED_EVENT', 'CROSS_REFERENCED_EVENT',
                'DEMILESTONED_EVENT', 'LABELED_EVENT', 'MARKED_AS_DUPLICATE_EVENT', 'MENTIONED_EVENT',
                'MILESTONED_EVENT', 'PINNED_EVENT', 'REFERENCED_EVENT', 'RENAMED_TITLE_EVENT', 'REOPENED_EVENT',
                'TRANSFERRED_EVENT', 'UNASSIGNED_EVENT', 'UNLABELED_EVENT', 'UNMARKED_AS_DUPLICATE_EVENT',
                'UNPINNED_EVENT')),
            CONSTRAINT added_enum_check CHECK (added_type IN ('USER', 'MILESTONE', 'LABEL', 'COMMIT_ID', 'TITLE',
                'REPOSITORY')),
            CONSTRAINT removed_enum_check CHECK (removed_type IN ('USER', 'MILESTONE', 'LABEL', 'COMMIT_ID', 'TITLE',
                'REPOSITORY'))
        )
        """
        self.issue_assignees = Table(
            'issue_assignees', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('assignee_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE"))
        )
    
        self.issue_labels = Table(
            'issue_labels', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('label_id', None, ForeignKey('labels.id', ondelete="CASCADE")),
        )
    
        self.issue_comments = Table(
            'issue_comments', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('commenter_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('body', TEXT, nullable=False),
            Column('created_at', DATETIME, nullable=False),
            Column('updated_at', DATETIME, nullable=False),
            Column('is_minimized', BOOLEAN, default=False),
            Column('minimized_reason', VARCHAR(255)),
            Column('positive_reaction_count', INTEGER, default=0, nullable=False),
            Column('negative_reaction_count', INTEGER, default=0, nullable=False),
            Column('ambiguous_reaction_count', INTEGER, default=0, nullable=False)
        )
    
        self.issue_events = Table(
            'issue_events', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('event_type', self._event_type_enum[0], nullable=False),
            Column('who', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('when', DATETIME, nullable=False),
            Column('added', VARCHAR(255)),
            Column('added_type', self._added_or_removed_type[0]),
            Column('removed', VARCHAR(255)),
            Column('removed_type', self._added_or_removed_type[0]),
            Column('is_cross_repository', BOOLEAN, default=0, nullable=False)
        )
    
        if self._event_type_enum[1]:
            self.issue_events.append_constraint(CheckConstraint(f"event_type IN ({self._get_string(EventType)})",
                                                                name='event_enum_check'))
    
        if self._added_or_removed_type[1]:
            self.issue_events.append_constraint(
                CheckConstraint(f"added_type IN ({self._get_string(AddedOrRemovedType)})", name='added_enum_check')
            )

            self.issue_events.append_constraint(
                CheckConstraint(f"removed_type IN ({self._get_string(AddedOrRemovedType)})", name='removed_enum_check')
            )
    
        self.issue_assignees.create(bind=self.conn, checkfirst=True)
        self.issue_labels.create(bind=self.conn, checkfirst=True)
        self.issue_comments.create(bind=self.conn, checkfirst=True)
        self.issue_events.create(bind=self.conn, checkfirst=True)
    
    @staticmethod
    def contributors_object(login, name, email, created_at, updated_at, location, total_followers=0,
                            is_anonymous=0):
        obj = {
            'login'          : get_value(login),
            'name'           : get_value(name),
            'email'          : get_value(email),
            'created_at'     : to_datetime(created_at),
            'updated_at'     : to_datetime(updated_at),
            'total_followers': total_followers,
            'location'       : get_value(location),
            'is_anonymous'   : is_anonymous
        }
        
        return obj
    
    @staticmethod
    def repository_object(name, owner, created_at, updated_at, description, disk_usage, fork_count, url,
                          homepage_url, primary_language, total_stargazers, total_watchers, forked_from):
        obj = {
            'name'            : name,
            'owner'           : owner,
            'created_at'      : to_datetime(created_at),
            'updated_at'      : to_datetime(updated_at),
            'description'     : get_value(description),
            'disk_usage'      : disk_usage,
            'fork_count'      : fork_count,
            'url'             : url,
            'homepage_url'    : get_value(homepage_url),
            'primary_language': get_value(primary_language),
            'total_stargazers': total_stargazers,
            'total_watchers'  : total_watchers,
            'forked_from'     : get_value(forked_from)
        }

        return obj

    @staticmethod
    def languages_object(repo_id, name, size):
        obj = {
            "repo_id": repo_id,
            "name"   : get_value(name),
            "size"   : size
        }
    
        return obj

    @staticmethod
    def milestones_object(number, repo_id, creator_id, title, description, due_on, closed_at, created_at, updated_at,
                          state):
        obj = {
            "number"     : number,
            "repo_id"    : repo_id,
            "creator_id" : creator_id,
            "title"      : get_value(title),
            "description": get_value(description),
            "due_on"     : to_datetime(due_on),
            "closed_at"  : to_datetime(closed_at),
            "created_at" : to_datetime(created_at),
            "updated_at" : to_datetime(updated_at),
            "state"      : get_value(state)
        }
    
        return obj

    @staticmethod
    def stargazers_object(repo_id, user_id, starred_at):
        obj = {
            "repo_id"   : repo_id,
            "user_id"   : user_id,
            "starred_at": to_datetime(starred_at)
        }
    
        return obj

    @staticmethod
    def watchers_object(repo_id, user_id):
        obj = {
            "repo_id": repo_id,
            "user_id": user_id
        }
    
        return obj

    @staticmethod
    def topics_object(repo_id, url, name, total_stargazers):
        obj = {
            "repo_id"         : repo_id,
            "url"             : get_value(url),
            "name"            : get_value(name),
            "total_stargazers": total_stargazers
        }
    
        return obj

    @staticmethod
    def releases_object(repo_id, creator_id, name, description, created_at, updated_at, is_prerelease, tag):
        obj = {
            "repo_id"      : repo_id,
            "creator_id"   : creator_id,
            "name"         : name,
            "description"  : get_value(description),
            "created_at"   : to_datetime(created_at),
            "updated_at"   : to_datetime(updated_at),
            "is_prerelease": is_prerelease,
            "tag"          : get_value(tag)
        }
    
        return obj

    @staticmethod
    def forks_object(repo_id, user_id, forked_at):
        obj = {
            "repo_id"  : repo_id,
            "user_id"  : user_id,
            "forked_at": to_datetime(forked_at)
        }
    
        return obj

    @staticmethod
    def branches_object(repo_id, name, target_commit_id):
        obj = {
            "repo_id"         : repo_id,
            "name"            : name,
            "target_commit_id": target_commit_id
        }
    
        return obj

    @staticmethod
    def labels_object(repo_id, name, color, created_at, type_):
        obj = {
            "repo_id"   : repo_id,
            "name"      : name,
            "color"     : get_value(color),
            "created_at": to_datetime(created_at),
            "type_"     : get_value(type_)
        }
    
        return obj

    @staticmethod
    def issues_object(number, repo_id, created_at, updated_at, closed_at, title, body, reporter_id, milestone_id,
                      positive_reaction_count, negative_reaction_count, ambiguous_reaction_count, state):
        obj = {
            "number"                  : number,
            "repo_id"                 : repo_id,
            "created_at"              : to_datetime(created_at),
            "updated_at"              : to_datetime(updated_at),
            "closed_at"               : to_datetime(closed_at),
            "title"                   : get_value(title),
            "body"                    : get_value(body),
            "reporter_id"             : reporter_id,
            "milestone_id"            : milestone_id,
            "positive_reaction_count" : positive_reaction_count,
            "negative_reaction_count" : negative_reaction_count,
            "ambiguous_reaction_count": ambiguous_reaction_count,
            "state"                   : get_value(state)
        }
    
        return obj

    @staticmethod
    def issue_assignees_object(repo_id, issue_id, assignee_id):
        obj = {
            "repo_id"    : repo_id,
            "issue_id"   : issue_id,
            "assignee_id": assignee_id
        }
    
        return obj

    @staticmethod
    def issue_labels_object(repo_id, issue_id, label_id):
        obj = {
            "repo_id" : repo_id,
            "issue_id": issue_id,
            "label_id": label_id
        }
    
        return obj

    @staticmethod
    def issue_comments_object(repo_id, issue_id, commenter_id, body, created_at, updated_at, is_minimized,
                              minimized_reason, positive_reaction_count, negative_reaction_count,
                              ambiguous_reaction_count):
        obj = {
            "repo_id"                 : repo_id,
            "issue_id"                : issue_id,
            "commenter_id"            : commenter_id,
            "body"                    : get_value(body),
            "created_at"              : to_datetime(created_at),
            "updated_at"              : to_datetime(updated_at),
            "is_minimized"            : is_minimized,
            "minimized_reason"        : get_value(minimized_reason),
            "positive_reaction_count" : positive_reaction_count,
            "negative_reaction_count" : negative_reaction_count,
            "ambiguous_reaction_count": ambiguous_reaction_count
        }
    
        return obj

    @staticmethod
    def issue_events_object(repo_id, issue_id, event_type, who, when, added, added_type, removed, removed_type,
                            is_cross_repository):
        obj = {
            "repo_id"            : repo_id,
            "issue_id"           : issue_id,
            "event_type"         : get_value(event_type),
            "who"                : who,
            "when"               : to_datetime(when),
            "added"              : added if isinstance(added, int) else get_value(added),
            "added_type"         : get_value(added_type),
            "removed"            : removed if isinstance(removed, int) else get_value(removed),
            "removed_type"       : get_value(removed_type),
            "is_cross_repository": is_cross_repository
        }
    
        return obj
