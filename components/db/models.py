import enum

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.schema import CheckConstraint, Column, ForeignKey, MetaData, Table, UniqueConstraint
from sqlalchemy.types import BOOLEAN, INTEGER, TEXT, TIMESTAMP, VARCHAR


def get_string(cls):
    return ", ".join(cls.__members__.keys())


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


class DBSchema:
    def __init__(self, engine):
        self.engine = engine
        self._metadata = MetaData()
        
        self._state_enum = self.__get_enum(State)
        self._label_enum = self.__get_enum(LabelType)
        self._event_type_enum = self.__get_enum(EventType)
        self._added_or_removed_type = self.__get_enum(AddedOrRemovedType)
        
        self._create_contributors_table()
        self._create_repository_table()
        self._create_repository_stats_tables()
        self._create_issue_table()
        self._create_issue_tracker_tables()
    
    def __get_enum(self, cls):
        if self.engine.name == "mysql":
            return ENUM(cls), False
        elif self.engine.name == "sqlite":
            return VARCHAR(255), True
        else:
            return ENUM(cls), False
    
    def _create_contributors_table(self):
        """
            CREATE TABLE contributors (
                contributor_id INTEGER NOT NULL, 
                login VARCHAR(255), 
                name VARCHAR(255), 
                email VARCHAR(255), 
                created_at TIMESTAMP NOT NULL, 
                updated_at TIMESTAMP NOT NULL, 
                total_followers INTEGER NOT NULL, 
                location VARCHAR(255), 
                is_anonymous BOOLEAN NOT NULL, 
                is_assignee BOOLEAN NOT NULL,
                
                PRIMARY KEY (contributor_id)
            )
        """
        
        contributors = Table(
            'contributors', self._metadata,
            Column('contributor_id', INTEGER, autoincrement=True, primary_key=True),
            Column('login', VARCHAR(255)),
            Column('name', VARCHAR(255)),
            Column('email', VARCHAR(255)),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP, nullable=False),
            Column('total_followers', INTEGER, nullable=False, default=0),
            Column('location', VARCHAR(255)),
            Column('is_anonymous', BOOLEAN, nullable=False, default=0),
            Column('is_assignee', BOOLEAN, nullable=False, default=0)
        )
        
        contributors.create(bind=self.engine, checkfirst=True)
    
    def _create_repository_table(self):
        """
            CREATE TABLE repository (
                repo_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                owner VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
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
        repository = Table(
            'repository', self._metadata,
            Column('repo_id', INTEGER, autoincrement=True, primary_key=True),
            Column('name', VARCHAR(255), nullable=False),
            Column('owner', VARCHAR(255), nullable=False),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP, nullable=False),
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
        
        repository.create(bind=self.engine, checkfirst=True)
    
    def _create_repository_stats_tables(self):
        """
        CREATE TABLE languages (
            repo_id INTEGER,
            name VARCHAR(255) NOT NULL,
            size INTEGER NOT NULL,
            
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE
        )
        
        CREATE TABLE milestones (
            id INTEGER,
            number INTEGER NOT NULL,
            repo_id INTEGER,
            creator_id INTEGER,
            title TEXT,
            description TEXT,
            due_on TIMESTAMP,
            closed_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            state VARCHAR(255) NOT NULL,
            
            PRIMARY KEY (id),
            CONSTRAINT num_repo_ind UNIQUE (number, repo_id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(creator_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE,
            CONSTRAINT enum_check CHECK ('state IN (OPEN, CLOSED)')
        )
        
        CREATE TABLE stargazers (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            login VARCHAR(255) NOT NULL,
            starred_at TIMESTAMP,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE
        )
        
        CREATE TABLE watchers (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            login VARCHAR(255) NOT NULL,
            created_at TIMESTAMP,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE
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
            description TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            is_prerelease BOOLEAN,
            tag VARCHAR(255),
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(creator_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE forks (
            id INTEGER NOT NULL,
            repo_id INTEGER,
            login VARCHAR(255) NOT NULL,
            created_at TIMESTAMP NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE
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
            color VARCHAR(255) NOT NULL,
            created_at TIMESTAMP NOT NULL,
            type VARCHAR(255),
            
            PRIMARY KEY (id),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            CONSTRAINT enum_check CHECK ('type IN (GENERAL, PRIORITY, SEVERITY, COMPONENT)')
        )
        """
        languages = Table(
            'languages', self._metadata,
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('name', VARCHAR(255), nullable=False),
            Column('size', INTEGER, default=0, nullable=False)
        )
        
        milestones = Table(
            'milestones', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('number', INTEGER),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('creator_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('title', TEXT),
            Column('description', TEXT),
            Column('due_on', TIMESTAMP),
            Column('closed_at', TIMESTAMP),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP),
            Column('state', self._state_enum[0], nullable=False),
            UniqueConstraint('number', 'repo_id', name='num_repo_ind')
        )
        
        if self._state_enum[1]:
            milestones.append_constraint(CheckConstraint(f"\'state IN ({get_string(State)})\'", 'enum_check'))
        
        stargazers = Table(
            'stargazers', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('login', VARCHAR(255), nullable=False),
            Column('starred_at', TIMESTAMP)
        )
        
        watchers = Table(
            'watchers', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('login', VARCHAR(255), nullable=False),
            Column('created_at', TIMESTAMP)
        )
        
        topics = Table(
            'topics', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('url', VARCHAR(255), nullable=False),
            Column('name', VARCHAR(255), nullable=False),
            Column('total_stargazers', INTEGER, default=0, nullable=False)
        )
        
        releases = Table(
            'releases', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('creator_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('description', TEXT),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP, nullable=False),
            Column('is_prerelease', BOOLEAN, default=0, nullable=False),
            Column('tag', VARCHAR(255))
        )
        
        forks = Table(
            'forks', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('login', VARCHAR(255), nullable=False),
            Column('created_at', TIMESTAMP, nullable=False),
        )
        
        branches = Table(
            'branches', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('name', VARCHAR(255), nullable=False),
            Column('target_commit_id', VARCHAR(255), nullable=False)
        )
        
        labels = Table(
            'labels', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('color', VARCHAR(255), nullable=False),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('type', self._label_enum[0], default="COMPONENT")
        )
        
        if self._label_enum[1]:
            labels.append_constraint(CheckConstraint(f"\'type IN ({get_string(LabelType)})\'", 'enum_check'))
        
        languages.create(bind=self.engine, checkfirst=True)
        milestones.create(bind=self.engine, checkfirst=True)
        stargazers.create(bind=self.engine, checkfirst=True)
        watchers.create(bind=self.engine, checkfirst=True)
        topics.create(bind=self.engine, checkfirst=True)
        releases.create(bind=self.engine, checkfirst=True)
        forks.create(bind=self.engine, checkfirst=True)
        branches.create(bind=self.engine, checkfirst=True)
        labels.create(bind=self.engine, checkfirst=True)
    
    def _create_issue_table(self):
        """
            CREATE TABLE issues (
                id INTEGER NOT NULL,
                number INTEGER,
                repo_id INTEGER,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                closed_at TIMESTAMP,
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
                FOREIGN KEY(milestone_id) REFERENCES milestones (id) ON DELETE CASCADE
            )
        """
        issues = Table(
            'issues', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('number', INTEGER),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP, nullable=False),
            Column('closed_at', TIMESTAMP),
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
            issues.append_constraint(CheckConstraint(f"\'state in ({get_string(State)})\'", name='enum_check'))
        
        issues.create(bind=self.engine, checkfirst=True)
    
    def _create_issue_tracker_tables(self):
        """
        CREATE TABLE issue_assignees (
            id INTEGER NOT NULL,
            issue_id INTEGER,
            assignee_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(assignee_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE issue_labels (
            id INTEGER NOT NULL,
            issue_id INTEGER,
            label_id INTEGER,
            
            PRIMARY KEY (id),
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(label_id) REFERENCES labels (id) ON DELETE CASCADE
        )
        
        CREATE TABLE issue_comments (
            id INTEGER NOT NULL,
            issue_id INTEGER,
            commenter_id INTEGER,
            body TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            is_minimized BOOLEAN,
            minimized_reason VARCHAR(255),
            positive_reaction_count INTEGER NOT NULL,
            negative_reaction_count INTEGER NOT NULL,
            ambiguous_reaction_count INTEGER NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(commenter_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE
        )
        
        CREATE TABLE issue_events (
            id INTEGER NOT NULL,
            issue_id INTEGER,
            event_type VARCHAR(255) NOT NULL,
            who INTEGER,
            "when" TIMESTAMP NOT NULL,
            added VARCHAR(255),
            added_type VARCHAR(255),
            removed VARCHAR(255),
            removed_type VARCHAR(255),
            is_cross_repository BOOLEAN NOT NULL,
            
            PRIMARY KEY (id),
            FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE,
            FOREIGN KEY(who) REFERENCES contributors (contributor_id) ON DELETE CASCADE,
            CONSTRAINT event_enum_check CHECK ('event_type in (ASSIGNED_EVENT, CROSS_REFERENCED_EVENT,
                DEMILESTONED_EVENT, LABELED_EVENT, MARKED_AS_DUPLICATE_EVENT, MENTIONED_EVENT, MILESTONED_EVENT,
                PINNED_EVENT, REFERENCED_EVENT, RENAMED_TITLE_EVENT, REOPENED_EVENT, TRANSFERRED_EVENT,
                UNASSIGNED_EVENT, UNLABELED_EVENT, UNMARKED_AS_DUPLICATE_EVENT, UNPINNED_EVENT)'),
            CONSTRAINT added_enum_check CHECK ('added_type in (USER, MILESTONE, LABEL, COMMIT_ID, TITLE, REPOSITORY)'),
            CONSTRAINT removed_enum_check CHECK ('removed_type in (USER, MILESTONE, LABEL, COMMIT_ID, TITLE,
                REPOSITORY)')
        )
        """
        issue_assignees = Table(
            'issue_assignees', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('assignee_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE"))
        )
        
        issue_labels = Table(
            'issue_labels', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('label_id', None, ForeignKey('labels.id', ondelete="CASCADE")),
        )
        
        issue_comments = Table(
            'issue_comments', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('commenter_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('body', TEXT, nullable=False),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP, nullable=False),
            Column('is_minimized', BOOLEAN, default=False),
            Column('minimized_reason', VARCHAR(255)),
            Column('positive_reaction_count', INTEGER, default=0, nullable=False),
            Column('negative_reaction_count', INTEGER, default=0, nullable=False),
            Column('ambiguous_reaction_count', INTEGER, default=0, nullable=False)
        )
        
        issue_events = Table(
            'issue_events', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('issue_id', None, ForeignKey('issues.id', ondelete="CASCADE")),
            Column('event_type', self._event_type_enum[0], nullable=False),
            Column('who', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('when', TIMESTAMP, nullable=False),
            Column('added', VARCHAR(255)),
            Column('added_type', self._added_or_removed_type[0]),
            Column('removed', VARCHAR(255)),
            Column('removed_type', self._added_or_removed_type[0]),
            Column('is_cross_repository', BOOLEAN, default=0, nullable=False)
        )
        
        if self._event_type_enum[1]:
            issue_events.append_constraint(CheckConstraint(f"\'event_type in ({get_string(EventType)})\'",
                                                           name='event_enum_check'))
        
        if self._added_or_removed_type[1]:
            issue_events.append_constraint(CheckConstraint(f"\'added_type in ({get_string(AddedOrRemovedType)})\'",
                                                           name='added_enum_check'))
            
            issue_events.append_constraint(CheckConstraint(f"\'removed_type in ({get_string(AddedOrRemovedType)})\'",
                                                           name='removed_enum_check'))

        issue_assignees.create(bind=self.engine, checkfirst=True)
        issue_labels.create(bind=self.engine, checkfirst=True)
        issue_comments.create(bind=self.engine, checkfirst=True)
        issue_events.create(bind=self.engine, checkfirst=True)


if __name__ == '__main__':
    eng = create_engine('sqlite:////home/mahen/PycharmProjects/GRAS/file.db')
    db_schema = DBSchema(engine=eng)
