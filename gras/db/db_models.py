import enum

from sqlalchemy import Unicode, UnicodeText
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.schema import CheckConstraint, Column, ForeignKey, MetaData, Table, UniqueConstraint
from sqlalchemy.types import BOOLEAN, DATETIME, INTEGER, TEXT, VARCHAR

from gras.utils import get_value, to_datetime

UNICODE = None
UNICODE_TEXT = None


class State(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PullRequestState(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MERGED = "MERGED"


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
    CLOSED_EVENT = "CLOSED_EVENT"


class ReviewDecision(enum.Enum):
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class IssueType(enum.Enum):
    ISSUE = "ISSUE"
    PULL_REQUEST = "PULL_REQUEST"


class UserType(enum.Enum):
    USER = "USER"
    ORGANIZATION = "ORGANIZATION"
    BOT = "BOT"


class DBSchema:
    def __init__(self, conn, engine):
        self.engine = engine
        self.conn = conn
        self._metadata = MetaData()

        self.__set_unicode_variable()

        self._state_enum = self.__get_enum(State)
        self._pr_state_enum = self.__get_enum(PullRequestState)
        self._label_enum = self.__get_enum(LabelType)
        self._event_type_enum = self.__get_enum(EventType)
        self._review_decision_enum = self.__get_enum(ReviewDecision)
        self._issue_type_enum = self.__get_enum(IssueType)
        self._user_type_enum = self.__get_enum(UserType)

    def __set_unicode_variable(self):
        global UNICODE, UNICODE_TEXT

        if self.engine == "mysql":
            UNICODE = Unicode(255, collation='utf8mb4_bin')
            UNICODE_TEXT = UnicodeText(collation='utf8m_bin')
        else:
            UNICODE = VARCHAR(255)
            UNICODE_TEXT = TEXT

    def __get_enum(self, cls):
        if self.engine.name == "mysql":
            return ENUM(cls), False
        elif self.engine.name == "sqlite":
            return VARCHAR(255), True
        else:
            return ENUM(cls), False

    def __get_large_text_type(self):
        if self.engine.name == "mysql":
            return UNICODE_TEXT
        elif self.engine.name == "sqlite":
            return TEXT
        else:
            return TEXT

    def __get_date_field(self):
        if self.engine.name == 'mysql':
            return DATETIME
        elif self.engine.name == "sqlite":
            return DATETIME
        else:
            return TIMESTAMP

    @staticmethod
    def _get_string(cls):
        return ", ".join(["\'" + x + "\'" for x in cls.__members__.keys()])

    def create_tables(self):
        self._create_contributors_table()
        self._create_repository_table()
        self._create_repository_stats_tables()
        self._create_issues_table()
        self._create_issue_tracker_tables()
        self._create_commit_tables()
        self._create_pr_table()
        self._create_pr_tracker_tables()

    def _create_contributors_table(self):
        """
        CREATE TABLE contributors (
            id INTEGER NOT NULL,
            contributor_id INTEGER,
            login VARCHAR(255),
            name VARCHAR(255),
            email VARCHAR(255),
            created_at DATETIME,
            updated_at DATETIME,
            total_followers INTEGER DEFAULT '0' NOT NULL,
            location VARCHAR(255),
            user_type VARCHAR(255) NOT NULL,
            is_anonymous BOOLEAN DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            CONSTRAINT login_email_ind UNIQUE (login, email),
            CHECK (is_anonymous IN (0, 1)),
            CONSTRAINT enum_check CHECK (user_type IN ('USER', 'ORGANIZATION', 'BOT'))
        )
        """
        self.contributors = Table(
            'contributors', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('contributor_id', INTEGER, server_default=None),
            Column('login', UNICODE),
            Column('name', UNICODE),
            Column('email', UNICODE),
            Column('created_at', self.__get_date_field()),
            Column('updated_at', self.__get_date_field()),
            Column('total_followers', INTEGER, nullable=False, server_default='0'),
            Column('location', UNICODE),
            Column('user_type', self._user_type_enum[0], nullable=False),
            Column('is_anonymous', BOOLEAN, nullable=False, server_default='0'),
            UniqueConstraint('login', 'email', name='login_email_ind')
        )

        if self._user_type_enum[1]:
            self.contributors.append_constraint(CheckConstraint(f"user_type IN ({self._get_string(UserType)})",
                                                                name='enum_check'))

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
            fork_count INTEGER DEFAULT '0' NOT NULL,
            url VARCHAR(255) NOT NULL,
            homepage_url VARCHAR(255) NOT NULL,
            primary_language VARCHAR(255) NOT NULL,
            total_stargazers INTEGER DEFAULT '0' NOT NULL,
            total_watchers INTEGER DEFAULT '0' NOT NULL,
            forked_from VARCHAR(255),
            
            PRIMARY KEY (repo_id),
            CONSTRAINT name_owner_ind UNIQUE (name, owner)
        )
        """
        self.repository = Table(
            'repository', self._metadata,
            Column('repo_id', INTEGER, autoincrement=True, primary_key=True),
            Column('name', UNICODE, nullable=False),
            Column('owner', UNICODE, nullable=False),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field(), nullable=False),
            Column('description', TEXT),
            Column('disk_usage', INTEGER, nullable=False),
            Column('fork_count', INTEGER, server_default='0', nullable=False),
            Column('url', UNICODE, nullable=False),
            Column('homepage_url', UNICODE),
            Column('primary_language', UNICODE, nullable=False),
            Column('total_stargazers', INTEGER, server_default='0', nullable=False),
            Column('total_watchers', INTEGER, server_default='0', nullable=False),
            Column('forked_from', UNICODE),
            UniqueConstraint('name', 'owner')
        )

        self.repository.create(bind=self.conn, checkfirst=True)

    def _create_repository_stats_tables(self):
        """
        CREATE TABLE languages (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            name VARCHAR(255) NOT NULL,
            size INTEGER DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE
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
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(creator_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT enum_check CHECK (state IN ('OPEN', 'CLOSED'))
        )
        
        CREATE TABLE stargazers (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            user_id INTEGER,
            starred_at DATETIME,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(user_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE watchers (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(user_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE topics (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            url VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            total_stargazers INTEGER DEFAULT '0' NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE releases (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            creator_id INTEGER,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_prerelease BOOLEAN DEFAULT '0' NOT NULL,
            tag VARCHAR(255),
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(creator_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CHECK (is_prerelease IN (0, 1))
        )
        
        CREATE TABLE forks (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            user_id INTEGER,
            forked_at DATETIME NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(user_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE branches (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            name VARCHAR(255) NOT NULL,
            target_commit_id VARCHAR(255) NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE labels (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            name VARCHAR(255) NOT NULL,
            color VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            label_type VARCHAR(255) NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT enum_check CHECK (label_type IN ('GENERAL', 'PRIORITY', 'SEVERITY', 'COMPONENT'))
        )
        """
        self.languages = Table(
            'languages', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('name', UNICODE, nullable=False),
            Column('size', INTEGER, server_default='0', nullable=False)
        )

        self.milestones = Table(
            'milestones', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('number', INTEGER),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('creator_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('title', TEXT),
            Column('description', TEXT),
            Column('due_on', self.__get_date_field()),
            Column('closed_at', self.__get_date_field()),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field()),
            Column('state', self._state_enum[0], nullable=False),
            UniqueConstraint('number', 'repo_id', name='num_repo_ind')
        )

        if self._state_enum[1]:
            self.milestones.append_constraint(CheckConstraint(f"state IN ({self._get_string(State)})",
                                                              name='enum_check'))

        self.stargazers = Table(
            'stargazers', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('user_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('starred_at', self.__get_date_field())
        )

        self.watchers = Table(
            'watchers', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('user_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE"))
        )

        self.topics = Table(
            'topics', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('url', UNICODE, nullable=False),
            Column('name', UNICODE, nullable=False),
            Column('total_stargazers', INTEGER, server_default='0', nullable=False)
        )

        self.releases = Table(
            'releases', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('creator_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('name', UNICODE, nullable=False),
            Column('description', TEXT),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field(), nullable=False),
            Column('is_prerelease', BOOLEAN, server_default='0', nullable=False),
            Column('tag', UNICODE)
        )

        self.forks = Table(
            'forks', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('user_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('forked_at', self.__get_date_field(), nullable=False),
        )

        self.branches = Table(
            'branches', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('name', UNICODE, nullable=False),
            Column('target_commit_id', UNICODE, nullable=False)
        )

        self.labels = Table(
            'labels', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('name', UNICODE, nullable=False),
            Column('color', UNICODE, nullable=False),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('label_type', self._label_enum[0], nullable=False)
        )

        if self._label_enum[1]:
            self.labels.append_constraint(CheckConstraint(f"label_type IN ({self._get_string(LabelType)})",
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
            positive_reaction_count INTEGER DEFAULT '0' NOT NULL,
            negative_reaction_count INTEGER DEFAULT '0' NOT NULL,
            ambiguous_reaction_count INTEGER DEFAULT '0' NOT NULL,
            state VARCHAR(255) NOT NULL,
            
            PRIMARY KEY (id),
            UNIQUE (number, repo_id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(reporter_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(milestone_id) REFERENCES milestones (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT enum_check CHECK (state IN ('OPEN', 'CLOSED'))
        )
        """
        self.issues = Table(
            'issues', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('number', INTEGER),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field(), nullable=False),
            Column('closed_at', self.__get_date_field()),
            Column('title', TEXT),
            Column('body', self.__get_large_text_type()),
            Column('reporter_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('milestone_id', None, ForeignKey('milestones.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('positive_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('negative_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('ambiguous_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('state', self._state_enum[0], nullable=False),
            UniqueConstraint('number', 'repo_id')
        )

        if self._state_enum[1]:
            self.issues.append_constraint(CheckConstraint(f"state IN ({self._get_string(State)})",
                                                          name='enum_check'))

        self.issues.create(bind=self.conn, checkfirst=True)

    def _create_issue_tracker_tables(self):
        """
        CREATE TABLE issue_comments (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            commenter_id INTEGER,
            body TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_minimized BOOLEAN DEFAULT '0',
            minimized_reason VARCHAR(255),
            positive_reaction_count INTEGER DEFAULT '0' NOT NULL,
            negative_reaction_count INTEGER DEFAULT '0' NOT NULL,
            ambiguous_reaction_count INTEGER DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(commenter_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CHECK (is_minimized IN (0, 1))
        )
        
        CREATE TABLE issue_assignees (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            assignee_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(assignee_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE issue_labels (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            label_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(label_id) REFERENCES labels (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE issue_events (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            issue_id INTEGER,
            event_type VARCHAR(255) NOT NULL,
            who INTEGER,
            "when" DATETIME NOT NULL,
            added TEXT,
            added_type VARCHAR(255),
            removed TEXT,
            removed_type VARCHAR(255),
            is_cross_repository BOOLEAN DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(who) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CHECK (is_cross_repository IN (0, 1)),
            CONSTRAINT event_enum_check CHECK (event_type IN ('ASSIGNED_EVENT', 'CROSS_REFERENCED_EVENT',
                'DEMILESTONED_EVENT', 'LABELED_EVENT', 'MARKED_AS_DUPLICATE_EVENT', 'MENTIONED_EVENT',
                'MILESTONED_EVENT', 'PINNED_EVENT', 'REFERENCED_EVENT', 'RENAMED_TITLE_EVENT', 'REOPENED_EVENT',
                'TRANSFERRED_EVENT', 'UNASSIGNED_EVENT', 'UNLABELED_EVENT', 'UNMARKED_AS_DUPLICATE_EVENT',
                'UNPINNED_EVENT')),
            CONSTRAINT added_enum_check CHECK (added_type IN ('USER', 'MILESTONE', 'LABEL', 'COMMIT_ID', 'TITLE',
                'REPOSITORY', 'ISSUE', 'PULL_REQUEST')),
            CONSTRAINT removed_enum_check CHECK (removed_type IN ('USER', 'MILESTONE', 'LABEL', 'COMMIT_ID', 'TITLE',
                'REPOSITORY', 'ISSUE', 'PULL_REQUEST'))
        )
        """
        self.issue_comments = Table(
            'issue_comments', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('commenter_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('body', self.__get_large_text_type(), nullable=False),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field(), nullable=False),
            Column('is_minimized', BOOLEAN, server_default='0'),
            Column('minimized_reason', UNICODE),
            Column('positive_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('negative_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('ambiguous_reaction_count', INTEGER, server_default='0', nullable=False)
        )

        self.issue_assignees = Table(
            'issue_assignees', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('assignee_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE"))
        )

        self.issue_labels = Table(
            'issue_labels', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('label_id', None, ForeignKey('labels.id', ondelete="CASCADE", onupdate="CASCADE")),
        )

        self.issue_events = Table(
            'issue_events', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('event_type', self._event_type_enum[0], nullable=False),
            Column('who', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('when', self.__get_date_field(), nullable=False),
            Column('added', self.__get_large_text_type()),
            Column('added_type', UNICODE),
            Column('removed', self.__get_large_text_type()),
            Column('removed_type', UNICODE),
            Column('is_cross_repository', BOOLEAN, server_default='0', nullable=False)
        )

        if self._event_type_enum[1]:
            self.issue_events.append_constraint(CheckConstraint(f"event_type IN ({self._get_string(EventType)})",
                                                                name='event_enum_check'))

        self.issue_comments.create(bind=self.conn, checkfirst=True)
        self.issue_assignees.create(bind=self.conn, checkfirst=True)
        self.issue_labels.create(bind=self.conn, checkfirst=True)
        self.issue_events.create(bind=self.conn, checkfirst=True)

    def _create_commit_tables(self):
        """
        CREATE TABLE commits (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            oid VARCHAR(255) NOT NULL,
            additions INTEGER DEFAULT '0' NOT NULL,
            deletions INTEGER DEFAULT '0' NOT NULL,
            author_id INTEGER,
            authored_date DATETIME NOT NULL,
            committer_id INTEGER,
            committer_date DATETIME NOT NULL,
            message TEXT,
            num_files_changed INTEGER DEFAULT '0',
            is_merge BOOLEAN DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(author_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(committer_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CHECK (is_merge IN (0, 1))
        )
        
        CREATE TABLE commit_comments (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            commenter_id INTEGER,
            body TEXT,
            commit_id INTEGER,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            path VARCHAR(255),
            position INTEGER,
            positive_reaction_count INTEGER DEFAULT '0' NOT NULL,
            negative_reaction_count INTEGER DEFAULT '0' NOT NULL,
            ambiguous_reaction_count INTEGER DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(commenter_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(commit_id) REFERENCES commits (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE code_change (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            commit_id INTEGER NOT NULL,
            filename VARCHAR(255) NOT NULL,
            additions INTEGER DEFAULT '0',
            deletions INTEGER DEFAULT '0',
            changes INTEGER DEFAULT '0',
            change_type VARCHAR(255),
            patch TEXT,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(commit_id) REFERENCES commits (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
        self.commits = Table(
            'commits', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('oid', UNICODE, nullable=False),
            Column('additions', INTEGER, server_default='0', nullable=False),
            Column('deletions', INTEGER, server_default='0', nullable=False),
            Column('author_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('authored_date', self.__get_date_field(), nullable=False),
            Column('committer_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('committer_date', self.__get_date_field(), nullable=False),
            Column('message', self.__get_large_text_type()),
            Column('num_files_changed', INTEGER, server_default='0'),
            Column('is_merge', BOOLEAN, nullable=False, server_default='0')
        )

        self.code_change = Table(
            'code_change', self._metadata,
            Column('id', INTEGER, primary_key=True, autoincrement=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('commit_id', None, ForeignKey('commits.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
            Column('filename', UNICODE, nullable=False),
            Column('additions', INTEGER, server_default='0'),
            Column('deletions', INTEGER, server_default='0'),
            Column('changes', INTEGER, server_default='0'),
            Column('change_type', VARCHAR(255)),
            Column('patch', self.__get_large_text_type())
        )

        self.commit_comments = Table(
            'commit_comments', self._metadata,
            Column('id', INTEGER, primary_key=True, autoincrement=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('commenter_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('body', self.__get_large_text_type()),
            Column('commit_id', None, ForeignKey('commits.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field(), nullable=False),
            Column('path', UNICODE),
            Column('position', INTEGER),
            Column('positive_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('negative_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('ambiguous_reaction_count', INTEGER, server_default='0', nullable=False)
        )

        self.commits.create(bind=self.conn, checkfirst=True)
        self.commit_comments.create(bind=self.conn, checkfirst=True)
        self.code_change.create(bind=self.conn, checkfirst=True)

    def _create_pr_table(self):
        """
        CREATE TABLE pull_requests (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            number INTEGER NOT NULL,
            title TEXT,
            body TEXT,
            author_id INTEGER,
            num_files_changed INTEGER DEFAULT '0',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            additions INTEGER DEFAULT '0' NOT NULL,
            deletions INTEGER DEFAULT '0' NOT NULL,
            base_ref_name VARCHAR(255),
            base_ref_commit_id INTEGER,
            head_ref_name VARCHAR(255),
            head_ref_commit_id INTEGER,
            closed BOOLEAN NOT NULL,
            closed_at DATETIME,
            merged BOOLEAN NOT NULL,
            merged_at DATETIME,
            merged_by INTEGER,
            milestone_id INTEGER,
            positive_reaction_count INTEGER DEFAULT '0' NOT NULL,
            negative_reaction_count INTEGER DEFAULT '0' NOT NULL,
            ambiguous_reaction_count INTEGER DEFAULT '0' NOT NULL,
            state VARCHAR(255) NOT NULL,
            review_decision VARCHAR(255),
            
            PRIMARY KEY (id),
            UNIQUE (number, repo_id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(author_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(base_ref_commit_id) REFERENCES commits (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(head_ref_commit_id) REFERENCES commits (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CHECK (closed IN (0, 1)),
            CHECK (merged IN (0, 1)),
            FOREIGN KEY(merged_by) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(milestone_id) REFERENCES milestones (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT enum_check CHECK (state IN ('OPEN', 'CLOSED', 'MERGED')),
            CONSTRAINT rd_enum_check CHECK (review_decision IN ('CHANGES_REQUESTED', 'APPROVED', 'REVIEW_REQUIRED'))
        )
        """
        self.pull_requests = Table(
            'pull_requests', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('number', INTEGER, nullable=False),
            Column('title', TEXT),
            Column('body', self.__get_large_text_type()),
            Column('author_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('num_files_changed', INTEGER, server_default='0'),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field(), nullable=False),
            Column('additions', INTEGER, server_default='0', nullable=False),
            Column('deletions', INTEGER, server_default='0', nullable=False),
            Column('base_ref_name', UNICODE),
            Column('base_ref_commit_id', None, ForeignKey('commits.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('head_ref_name', UNICODE),
            Column('head_ref_commit_id', None, ForeignKey('commits.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('closed', BOOLEAN, nullable=False),
            Column('closed_at', self.__get_date_field()),
            Column('merged', BOOLEAN, nullable=False),
            Column('merged_at', self.__get_date_field()),
            Column('merged_by', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('milestone_id', None, ForeignKey('milestones.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('positive_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('negative_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('ambiguous_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('state', self._state_enum[0], nullable=False),
            Column('review_decision', self._review_decision_enum[0]),
            UniqueConstraint('number', 'repo_id')
        )

        if self._state_enum[1]:
            self.pull_requests.append_constraint(CheckConstraint(f"state IN ({self._get_string(PullRequestState)})",
                                                                 name='enum_check'))

        if self._review_decision_enum[1]:
            self.pull_requests.append_constraint(CheckConstraint(f"review_decision IN ("
                                                                 f"{self._get_string(ReviewDecision)})",
                                                                 name="rd_enum_check"))

        self.pull_requests.create(bind=self.conn, checkfirst=True)

    def _create_pr_tracker_tables(self):
        """
        CREATE TABLE pull_request_comments (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            pr_id INTEGER,
            commenter_id INTEGER,
            body TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_minimized BOOLEAN DEFAULT '0',
            minimized_reason VARCHAR(255),
            positive_reaction_count INTEGER DEFAULT '0' NOT NULL,
            negative_reaction_count INTEGER DEFAULT '0' NOT NULL,
            ambiguous_reaction_count INTEGER DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(pr_id) REFERENCES pull_requests (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(commenter_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CHECK (is_minimized IN (0, 1))
        )
        
        CREATE TABLE pull_request_commits (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            pr_id INTEGER,
            commit_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(pr_id) REFERENCES pull_requests (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(commit_id) REFERENCES commits (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE pull_request_assignees (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            pr_id INTEGER,
            assignee_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(pr_id) REFERENCES pull_requests (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(assignee_id) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE pull_request_labels (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            pr_id INTEGER,
            label_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(pr_id) REFERENCES pull_requests (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(label_id) REFERENCES labels (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        
        CREATE TABLE pull_request_events (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            pr_id INTEGER,
            event_type VARCHAR(255) NOT NULL,
            who INTEGER,
            "when" DATETIME NOT NULL,
            added TEXT,
            added_type VARCHAR(255),
            removed TEXT,
            removed_type VARCHAR(255),
            is_cross_repository BOOLEAN DEFAULT '0' NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(pr_id) REFERENCES pull_requests (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(who) REFERENCES contributors (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CHECK (is_cross_repository IN (0, 1)),
            CONSTRAINT event_enum_check CHECK (event_type IN ('ASSIGNED_EVENT', 'CROSS_REFERENCED_EVENT',
                'DEMILESTONED_EVENT', 'LABELED_EVENT', 'MARKED_AS_DUPLICATE_EVENT', 'MENTIONED_EVENT',
                'MILESTONED_EVENT', 'PINNED_EVENT', 'REFERENCED_EVENT', 'RENAMED_TITLE_EVENT', 'REOPENED_EVENT',
                'TRANSFERRED_EVENT', 'UNASSIGNED_EVENT', 'UNLABELED_EVENT', 'UNMARKED_AS_DUPLICATE_EVENT',
                'UNPINNED_EVENT')),
            CONSTRAINT added_enum_check CHECK (added_type IN ('USER', 'MILESTONE', 'LABEL', 'COMMIT_ID', 'TITLE',
                'REPOSITORY', 'ISSUE', 'PULL_REQUEST')),
            CONSTRAINT removed_enum_check CHECK (removed_type IN ('USER', 'MILESTONE', 'LABEL', 'COMMIT_ID', 'TITLE',
                'REPOSITORY', 'ISSUE', 'PULL_REQUEST'))
        )
        """
        self.pull_request_comments = Table(
            'pull_request_comments', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('pr_id', None, ForeignKey('pull_requests.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('commenter_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('body', self.__get_large_text_type(), nullable=False),
            Column('created_at', self.__get_date_field(), nullable=False),
            Column('updated_at', self.__get_date_field(), nullable=False),
            Column('is_minimized', BOOLEAN, server_default='0'),
            Column('minimized_reason', UNICODE),
            Column('positive_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('negative_reaction_count', INTEGER, server_default='0', nullable=False),
            Column('ambiguous_reaction_count', INTEGER, server_default='0', nullable=False)
        )

        self.pull_request_assignees = Table(
            'pull_request_assignees', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('pr_id', None, ForeignKey('pull_requests.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('assignee_id', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE"))
        )

        self.pull_request_labels = Table(
            'pull_request_labels', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('pr_id', None, ForeignKey('pull_requests.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('label_id', None, ForeignKey('labels.id', ondelete="CASCADE", onupdate="CASCADE")),
        )

        self.pull_request_commits = Table(
            'pull_request_commits', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('pr_id', None, ForeignKey('pull_requests.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('commit_id', None, ForeignKey('commits.id', ondelete="CASCADE", onupdate="CASCADE")),
        )

        self.pull_request_events = Table(
            'pull_request_events', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('pr_id', None, ForeignKey('pull_requests.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('event_type', self._event_type_enum[0], nullable=False),
            Column('who', None, ForeignKey('contributors.id', ondelete="CASCADE", onupdate="CASCADE")),
            Column('when', self.__get_date_field(), nullable=False),
            Column('added', self.__get_large_text_type()),
            Column('added_type', UNICODE),
            Column('removed', self.__get_large_text_type()),
            Column('removed_type', VARCHAR),
            Column('is_cross_repository', BOOLEAN, server_default='0', nullable=False)
        )

        if self._event_type_enum[1]:
            self.pull_request_events.append_constraint(CheckConstraint(f"event_type IN ({self._get_string(EventType)})",
                                                                       name='event_enum_check'))

        self.pull_request_comments.create(bind=self.conn, checkfirst=True)
        self.pull_request_commits.create(bind=self.conn, checkfirst=True)
        self.pull_request_assignees.create(bind=self.conn, checkfirst=True)
        self.pull_request_labels.create(bind=self.conn, checkfirst=True)
        self.pull_request_events.create(bind=self.conn, checkfirst=True)

    @staticmethod
    def contributors_object(user_type, login, name, email, created_at, updated_at, location, total_followers=0,
                            is_anonymous=0, contributor_id=None):
        obj = {
            'contributor_id' : contributor_id,
            'login'          : get_value(login),
            'name'           : get_value(name),
            'email'          : get_value(email),
            'created_at'     : to_datetime(created_at),
            'updated_at'     : to_datetime(updated_at),
            'total_followers': total_followers,
            'location'       : get_value(location),
            'user_type'      : get_value(user_type).upper(),
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
            "name"            : get_value(name),
            "target_commit_id": target_commit_id
        }

        return obj

    @staticmethod
    def labels_object(repo_id, name, color, created_at, label_type):
        obj = {
            "repo_id"   : repo_id,
            "name"      : get_value(name),
            "color"     : get_value(color),
            "created_at": to_datetime(created_at),
            "label_type": get_value(label_type)
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
    def pull_requests_object(repo_id, number, title, body, author_id, num_files_changed, created_at, updated_at,
                             additions, deletions, base_ref_name, base_ref_commit_id, head_ref_name,
                             head_ref_commit_id, closed, closed_at, merged, merged_at, merged_by, milestone_id,
                             positive_reaction_count, negative_reaction_count, ambiguous_reaction_count, state,
                             review_decision):
        obj = {
            "repo_id"                 : repo_id,
            "number"                  : number,
            "title"                   : get_value(title),
            "body"                    : get_value(body),
            "author_id"               : author_id,
            "num_files_changed"       : num_files_changed,
            "created_at"              : to_datetime(created_at),
            "updated_at"              : to_datetime(updated_at),
            "additions"               : additions,
            "deletions"               : deletions,
            "base_ref_name"           : get_value(base_ref_name),
            "base_ref_commit_id"      : base_ref_commit_id,
            "head_ref_name"           : get_value(head_ref_name),
            "head_ref_commit_id"      : head_ref_commit_id,
            "closed"                  : closed,
            "closed_at"               : to_datetime(closed_at),
            "merged"                  : merged,
            "merged_at"               : to_datetime(merged_at),
            "merged_by"               : merged_by,
            "milestone_id"            : milestone_id,
            "positive_reaction_count" : positive_reaction_count,
            "negative_reaction_count" : negative_reaction_count,
            "ambiguous_reaction_count": ambiguous_reaction_count,
            "state"                   : get_value(state),
            "review_decision"         : get_value(review_decision)
        }

        return obj

    @staticmethod
    def pull_request_comments_object(repo_id, pr_id, commenter_id, body, created_at, updated_at, is_minimized,
                                     minimized_reason, positive_reaction_count, negative_reaction_count,
                                     ambiguous_reaction_count):
        obj = {
            "repo_id"                 : repo_id,
            "pr_id"                   : pr_id,
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
    def pull_request_assignee_object(repo_id, pr_id, assignee_id):
        obj = {
            "repo_id"    : repo_id,
            "pr_id"      : pr_id,
            "assignee_id": assignee_id
        }

        return obj

    @staticmethod
    def pull_request_labels_object(repo_id, pr_id, label_id):
        obj = {
            "repo_id" : repo_id,
            "pr_id"   : pr_id,
            "label_id": label_id
        }

        return obj

    @staticmethod
    def pull_request_commits_object(repo_id, pr_id, commit_id):
        obj = {
            "repo_id"  : repo_id,
            "pr_id"    : pr_id,
            "commit_id": commit_id
        }

        return obj

    @staticmethod
    def pull_request_events_object(repo_id, pr_id, event_type, who, when, added, added_type, removed, removed_type,
                                   is_cross_repository):
        obj = {
            "repo_id"            : repo_id,
            "pr_id"              : pr_id,
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

    @staticmethod
    def commits_object(repo_id, oid, additions, deletions, author_id, authored_date, committer_id, committer_date,
                       message, num_files_changed, is_merge):
        obj = {
            "repo_id"          : repo_id,
            "oid"              : oid,
            "additions"        : additions,
            "deletions"        : deletions,
            "author_id"        : author_id,
            "authored_date"    : to_datetime(authored_date),
            "committer_id"     : committer_id,
            "committer_date"   : to_datetime(committer_date),
            "message"          : get_value(message),
            "num_files_changed": num_files_changed,
            "is_merge"         : is_merge
        }

        return obj

    @staticmethod
    def code_change_object(repo_id, commit_id, filename, additions, deletions, changes, change_type, patch):
        obj = {
            "repo_id"    : repo_id,
            "commit_id"  : commit_id,
            "filename"   : get_value(filename),
            "additions"  : additions,
            "deletions"  : deletions,
            "changes"    : changes,
            "change_type": get_value(change_type),
            "patch"      : patch
        }

        return obj

    @staticmethod
    def commit_comments_object(repo_id, commenter_id, body, commit_id, created_at, updated_at, path, position,
                               positive_reaction_count, negative_reaction_count, ambiguous_reaction_count):
        obj = {
            "repo_id"                 : repo_id,
            "commenter_id"            : commenter_id,
            "body"                    : get_value(body),
            "commit_id"               : commit_id,
            "created_at"              : to_datetime(created_at),
            "updated_at"              : to_datetime(updated_at),
            "path"                    : get_value(path),
            "position"                : position,
            "positive_reaction_count" : positive_reaction_count,
            "negative_reaction_count" : negative_reaction_count,
            "ambiguous_reaction_count": ambiguous_reaction_count
        }

        return obj
