import enum

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.schema import CheckConstraint, Column, CreateTable, ForeignKey, MetaData, Table, UniqueConstraint
from sqlalchemy.types import BOOLEAN, INTEGER, TEXT, TIMESTAMP, VARCHAR


class State(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    
    __str__ = f"({OPEN}, {CLOSED})"


class LabelType(enum.Enum):
    GENERAL = "GENERAL"
    PRIORITY = "PRIORITY"
    SEVERITY = "SEVERITY"
    COMPONENT = "COMPONENT"
    
    __str__ = f"({GENERAL}, {PRIORITY}, {SEVERITY}, {COMPONENT})"


class DBSchema:
    def __init__(self, engine):
        self.engine = engine
        self._metadata = MetaData()
        
        self._state_enum = self.__get_enum(State)
        self._label_enum = self.__get_enum(LabelType)
        
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
            PRIMARY KEY (number),
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
            Column('id', INTEGER, autoincrement=True),
            Column('number', INTEGER, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('creator_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('title', TEXT),
            Column('description', TEXT),
            Column('due_on', TIMESTAMP),
            Column('closed_at', TIMESTAMP),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP),
            Column('state', self._state_enum[0], nullable=False),
            UniqueConstraint('number', 'repo_id', name='num_repo_ind'),
        )
        
        if self._state_enum[1]:
            milestones.append_constraint(CheckConstraint(f"\'state IN {State.__str__}\'", 'enum_check'))
        
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
            Column('is_prerelease', BOOLEAN, default=0),
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
            labels.append_constraint(CheckConstraint(f"\'type IN {LabelType.__str__}\'", 'enum_check'))
        
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
            number INTEGER NOT NULL,
            repo_id INTEGER,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            closed_at TIMESTAMP,
            title TEXT,
            body TEXT,
            reporter_id INTEGER,
            milestone_id INTEGER,
            positive_reaction_count INTEGER,
            negative_reaction_count INTEGER,
            ambiguous_reaction_count INTEGER,
            state VARCHAR(255) NOT NULL,
            PRIMARY KEY (id, number),
            FOREIGN KEY(repo_id) REFERENCES repository (repo_id) ON DELETE CASCADE,
            FOREIGN KEY(reporter_id) REFERENCES contributors (contributor_id) ON DELETE CASCADE,
            FOREIGN KEY(milestone_id) REFERENCES milestones (number) ON DELETE CASCADE,
            CONSTRAINT enum_check CHECK ('state in (OPEN, CLOSED)')
        )
        """
        issues = Table(
            'issues', self._metadata,
            Column('id', INTEGER, autoincrement=True, primary_key=True),
            Column('number', INTEGER, primary_key=True),
            Column('repo_id', None, ForeignKey('repository.repo_id', ondelete="CASCADE")),
            Column('created_at', TIMESTAMP, nullable=False),
            Column('updated_at', TIMESTAMP, nullable=False),
            Column('closed_at', TIMESTAMP),
            Column('title', TEXT),
            Column('body', TEXT),
            Column('reporter_id', None, ForeignKey('contributors.contributor_id', ondelete="CASCADE")),
            Column('milestone_id', None, ForeignKey('milestones.number', ondelete="CASCADE")),
            Column('positive_reaction_count', INTEGER, default=0),
            Column('negative_reaction_count', INTEGER, default=0),
            Column('ambiguous_reaction_count', INTEGER, default=0),
            Column('state', self._state_enum[0], nullable=False)
        )
        
        if self._state_enum[1]:
            issues.append_constraint(CheckConstraint(f"\'state in {State.__str__}\'", name='enum_check'))
        
        issues.create(bind=self.engine, checkfirst=True)
    
    def _create_issue_tracker_tables(self):
        """
        """
        pass


if __name__ == '__main__':
    eng = create_engine('sqlite:////home/mahen/PycharmProjects/GRAS/file.db')
    db_schema = DBSchema(engine=eng)
