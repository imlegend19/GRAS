import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, ProgrammingError

from components.base_miner import BaseMiner
from components.db.models import DBSchema
from components.query_engine.entity.github_models import AnonContributorModel
from components.query_engine.structs.branch_struct import BranchStruct
from components.query_engine.structs.contributor_struct import (
    ContributorList, UserNodesStruct, UserStruct,
    UserStructV3
)
from components.query_engine.structs.event_struct import EventStruct
from components.query_engine.structs.fork_struct import ForkStruct
from components.query_engine.structs.issue_comment_struct import IssueCommentStruct
from components.query_engine.structs.issue_struct import IssueStruct
from components.query_engine.structs.label_struct import LabelStruct
from components.query_engine.structs.language_struct import LanguageStruct
from components.query_engine.structs.milestone_struct import MilestoneStruct
from components.query_engine.structs.release_struct import ReleaseStruct
from components.query_engine.structs.repository_struct import RepositoryStruct
from components.query_engine.structs.stargazer_struct import StargazerStruct
from components.query_engine.structs.topic_struct import TopicStruct
from components.query_engine.structs.watcher_struct import WatcherStruct

logger = logging.getLogger("main")
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


class GithubMiner(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)
        
        self._connect_to_db()
        self.db_schema = DBSchema(conn=self._conn, engine=self._engine)
    
    def _load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass
    
    def process(self):
        self.db_schema.create_tables()
    
        # node_ids = self._dump_anon_users()
        # self._dump_users(node_ids=node_ids, login=None)
        self._dump_repository()
        # self._dump_languages()
        # self._dump_milestones()
        # self._dump_stargazers()
        # self._dump_watchers()
        # self._dump_forks()
        # self._dump_topics()
        # self._dump_releases()
        # self._dump_labels()
        self._dump_issues()
    
        self._refactor_table(id_='contributor_id', table="contributors", group_by="login, name, email")
        self._refactor_table(id_='id', table='languages', group_by="repo_id, name")
        self._refactor_table(id_='id', table='milestones', group_by="repo_id, number")
        self._refactor_table(id_='id', table='stargazers', group_by="repo_id, user_id")
        self._refactor_table(id_='id', table='watchers', group_by="repo_id, user_id")
        self._refactor_table(id_='id', table='forks', group_by="repo_id, user_id")
        self._refactor_table(id_='id', table='topics', group_by="repo_id, url")
        self._refactor_table(id_='id', table='releases', group_by="repo_id, creator_id")
        self._refactor_table(id_='id', table='labels', group_by="repo_id, name")
        self._refactor_table(id_='id', table='issues', group_by="repo_id, number")
        self._refactor_table(id_='id', table='issue_assignees', group_by="repo_id, issue_id, assignee_id")
        self._refactor_table(id_='id', table='issue_labels', group_by='repo_id, issue_id, label_id')
        self._refactor_table(id_='id', table='issue_events', group_by='repo_id, issue_id, event_type, who, when')
    
        self._close_the_db()
    
    def _dump_anon_users(self):
        cont_list = ContributorList(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        node_ids = []
        obj_list = []
        
        for cont in cont_list.process():
            if isinstance(cont, AnonContributorModel):
                obj = self.db_schema.contributors_object(
                    login=None,
                    name=cont.name,
                    email=cont.email,
                    created_at=None,
                    updated_at=None,
                    total_followers=0,
                    location=None,
                    is_anonymous=1
                )
                
                obj_list.append(obj)
            else:
                node_ids.append("\"" + cont + "\"")

        logger.info("Dumping Anonymous Contributors...")
        self._insert(self.db_schema.contributors.insert(), obj_list)
        
        return node_ids
    
    def _dump_users(self, login, node_ids=None, user_object=None):
        if node_ids:
            assert isinstance(node_ids, list)
            
            for i in range(0, len(node_ids), 100):
                ids_str = ",".join(node_ids[i:i + 100])
                users = UserNodesStruct(
                    github_token=self.token,
                    node_ids=ids_str
                )
                
                obj_list = []
                for node in users.process():
                    obj = self.db_schema.contributors_object(
                        login=node.login,
                        name=node.name,
                        email=node.email,
                        created_at=node.created_at,
                        updated_at=node.updated_at,
                        total_followers=node.total_followers,
                        location=node.location
                    )

                    obj_list.append(obj)
                
                logger.info("Dumping Other Contributors...")
                self._insert(self.db_schema.contributors.insert(), obj_list)
        elif login:
            # TODO: Change the error thrown by UserStruct
            try:
                user = UserStruct(
                    github_token=self.token,
                    login=login
                ).process()
            except KeyError:
                user = UserStructV3(
                    github_token=self.token,
                    login=login
                ).process()
            
            if not user:
                user = UserStructV3(
                    github_token=self.token,
                    login=login
                ).process()
            
            obj = self.db_schema.contributors_object(
                login=login,
                name=user.name,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
                total_followers=user.total_followers,
                location=user.location,
                is_anonymous=0
            )
            
            logger.debug(f"Dumping User with login: {login}")
            self._insert(self.db_schema.contributors.insert(), obj)
        elif user_object:
            obj = self.db_schema.contributors_object(
                login=user_object.login,
                name=user_object.name,
                email=user_object.email,
                created_at=user_object.created_at,
                updated_at=user_object.updated_at,
                total_followers=user_object.total_followers,
                location=user_object.location,
                is_anonymous=0
            )
            
            logger.debug(f"Dumping User with login: {user_object.login}")
            self._insert(self.db_schema.contributors.insert(), obj)
        else:
            raise TypeError
    
    def _dump_repository(self):
        repo = RepositoryStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        ).process()
        
        obj = self.db_schema.repository_object(
            name=self.repo_name,
            owner=self.repo_owner,
            created_at=repo.created_at,
            updated_at=repo.updated_at,
            description=repo.description,
            disk_usage=repo.disk_usage,
            fork_count=repo.fork_count,
            url=repo.url,
            homepage_url=repo.homepage_url,
            primary_language=repo.primary_language,
            total_stargazers=repo.stargazer_count,
            total_watchers=repo.watcher_count,
            forked_from=repo.forked_from
        )

        logger.info("Dumping Repository...")
        self._insert(self.db_schema.repository.insert(), obj)
        self._set_repo_id()
    
    def _dump_languages(self):
        lang = LanguageStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        for node in lang.process():
            obj = self.db_schema.languages_object(
                repo_id=self.repo_id,
                name=node.language,
                size=node.size
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Languages...")
        self._insert(self.db_schema.languages.insert(), obj_list)
    
    def _dump_milestones(self):
        milestones = MilestoneStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        for node in milestones.process():
            obj = self.db_schema.milestones_object(
                number=node.number,
                repo_id=self.repo_id,
                creator_id=self._get_user_id(node.creator_login),
                title=node.title,
                description=node.description,
                due_on=node.due_on,
                closed_at=node.closed_at,
                created_at=node.created_at,
                updated_at=node.updated_at,
                state=node.state
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Milestones...")
        self._insert(self.db_schema.milestones.insert(), obj_list)
    
    def _dump_stargazers(self):
        stargazers = StargazerStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        
        for node in stargazers.process():
            obj = self.db_schema.stargazers_object(
                repo_id=self.repo_id,
                user_id=self._get_user_id(login=None, user_object=node.user),
                starred_at=node.starred_at
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Stargazers...")
        self._insert(self.db_schema.stargazers.insert(), obj_list)
    
    def _dump_watchers(self):
        watchers = WatcherStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        
        for node in watchers.process():
            obj = self.db_schema.watchers_object(
                repo_id=self.repo_id,
                user_id=self._get_user_id(login=None, user_object=node.user)
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Watchers...")
        self._insert(self.db_schema.watchers.insert(), obj_list)
    
    def _dump_forks(self):
        forks = ForkStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        
        for node in forks.process():
            obj = self.db_schema.forks_object(
                repo_id=self.repo_id,
                user_id=self._get_user_id(login=None, user_object=node.user),
                forked_at=node.forked_at
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Forks...")
        self._insert(self.db_schema.forks.insert(), obj_list)
    
    def _dump_topics(self):
        topics = TopicStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        
        for node in topics.process():
            obj = self.db_schema.topics_object(
                repo_id=self.repo_id,
                name=node.topic_name,
                total_stargazers=node.stargazer_count,
                url=node.url
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Topics...")
        self._insert(self.db_schema.topics.insert(), obj_list)
    
    def _dump_releases(self):
        releases = ReleaseStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        
        for node in releases.process():
            obj = self.db_schema.releases_object(
                repo_id=self.repo_id,
                creator_id=self._get_user_id(node.author_login),
                name=node.name,
                description=node.description,
                created_at=node.created_at,
                updated_at=node.updated_at,
                is_prerelease=node.is_prerelease,
                tag=node.tag_name
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Releases...")
        self._insert(self.db_schema.releases.insert(), obj_list)
    
    def _dump_branches(self):
        branches = BranchStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        
        for node in branches.process():
            obj = self.db_schema.branches_object(
                repo_id=self.repo_id,
                name=node.name,
                target_commit_id=node.commit_id
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Branches...")
        self._insert(self.db_schema.branches.insert(), obj_list)
    
    def _dump_labels(self):
        # TODO: Set label types as per user
        labels = LabelStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner
        )
        
        obj_list = []
        
        for node in labels.process():
            obj = self.db_schema.labels_object(
                repo_id=self.repo_id,
                name=node.name,
                color=node.color,
                created_at=node.created_at,
                type_="GENERAL"
            )
            
            obj_list.append(obj)
        
        logger.info("Dumping Labels...")
        self._insert(self.db_schema.labels.insert(), obj_list)
    
    def _dump_issue_assignees(self, node_list):
        obj_list = []
        
        for node in node_list:
            issue_id = node[0]
            for assignee_login in node[1]:
                obj = self.db_schema.issue_assignees_object(
                    repo_id=self.repo_id,
                    issue_id=issue_id,
                    assignee_id=self._get_user_id(login=assignee_login)
                )
                
                obj_list.append(obj)
        
        logger.info("Dumping Issue Assignees...")
        self._insert(self.db_schema.issue_assignees.insert(), obj_list)
    
    def _dump_issue_labels(self, label_list):
        obj_list = []
        
        for node in label_list:
            issue_id = node[0]
            for label_name in node[1]:
                obj = self.db_schema.issue_labels_object(
                    repo_id=self.repo_id,
                    issue_id=issue_id,
                    label_id=self._get_table_id('labels', 'name', label_name)
                )
                
                obj_list.append(obj)
        
        logger.info("Dumping Issue Labels...")
        self._insert(self.db_schema.issue_labels.insert(), obj_list)
    
    def _dump_issue_events(self, issue_list):
        logger.info("Dumping Issue Events...")
        for number in issue_list:
            issue_event = EventStruct(
                github_token=self.token,
                name=self.repo_name,
                owner=self.repo_owner,
                since=self.start_date,
                type_filter="issue",
                number=number
            )
            
            issue_id = self._get_table_id(table="issues", field="number", value=number)
            
            obj_list = []
            
            for node in issue_event.process():
                obj = self.db_schema.issue_events_object(
                    repo_id=self.repo_id,
                    issue_id=issue_id,
                    event_type=node.event_type,
                    who=self._get_user_id(login=node.who),
                    when=node.when,
                    added=node.added,
                    added_type=node.added_type,
                    removed=node.removed,
                    removed_type=node.removed_type,
                    is_cross_repository=node.is_cross_repository
                )
                
                obj_list.append(obj)
            
            logger.debug(f"Dumping Issue Events for Issue Number: {number}...")
            self._insert(object_=self.db_schema.issue_events.insert(), param=obj_list)
    
    def _dump_issue_comments(self, issue_list):
        logger.info("Dumping Issue Comments...")
        for number in issue_list:
            issue_comments = IssueCommentStruct(
                github_token=self.token,
                name=self.repo_name,
                owner=self.repo_owner,
                number=number
            )
            
            issue_id = self._get_table_id(table="issues", field="number", value=number)
            
            obj_list = []
            
            for node in issue_comments.process():
                obj = self.db_schema.issue_comments_object(
                    repo_id=self.repo_id,
                    issue_id=issue_id,
                    commenter_id=self._get_user_id(login=node.author_login),
                    body=node.body,
                    created_at=node.created_at,
                    updated_at=node.updated_at,
                    is_minimized=node.is_minimized,
                    minimized_reason=node.minimized_reason,
                    positive_reaction_count=node.positive_reaction_count,
                    negative_reaction_count=node.negative_reaction_count,
                    ambiguous_reaction_count=node.ambiguous_reaction_count
                )
                
                obj_list.append(obj)
            
            logger.debug(f"Dumping Issue Comments for Issue Number: {number}...")
            self._insert(object_=self.db_schema.issue_comments.insert(), param=obj_list)
    
    def _dump_issues(self):
        # TODO: Add _dump_issue_assignees and _dump_issue_labels
        logger.info("Dumping Issues...")
        
        issues = IssueStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        obj_list = []
        issue_assignees_lst = []
        issue_labels_lst = []
        issue_list = []
        
        for node in issues.process():
            obj = self.db_schema.issues_object(
                number=node.number,
                repo_id=self.repo_id,
                created_at=node.created_at,
                updated_at=node.updated_at,
                closed_at=node.closed_at,
                title=node.title,
                body=node.body,
                reporter_id=self._get_user_id(login=node.author_login),
                milestone_id=self._get_table_id(table='milestones', field='number', value=node.milestone_number),
                positive_reaction_count=node.positive_reaction_count,
                negative_reaction_count=node.negative_reaction_count,
                ambiguous_reaction_count=node.ambiguous_reaction_count,
                state=node.state
            )
            
            issue_assignees_lst.append((node.number, node.assignees))
            issue_labels_lst.append((node.number, node.labels))
            issue_list.append(node.number)
            
            obj_list.append(obj)
        
        logger.info(f"Total Issues: {len(issue_list)}...")
        self._insert(self.db_schema.issues.insert(), obj_list)
        
        self._dump_issue_assignees(issue_assignees_lst)
        self._dump_issue_labels(issue_labels_lst)
        self._dump_issue_events(issue_list)
        self._dump_issue_comments(issue_list)
    
    def _refactor_table(self, id_, table, group_by):
        logger.info(f"Refactoring Table: {table}")
        
        self._conn.execute(
            f"""
            DELETE FROM {table}
            WHERE {id_} IN (
                SELECT max({id_}) FROM {table}
                GROUP BY {group_by}
                HAVING count(*) > 1
            )
            """
        )
        
        self._reorder_table(id_=id_, table=table)
    
    def _reorder_table(self, id_, table):
        logger.debug(f"Reordering Table: {table}")
        
        table_ids = self._conn.execute(f"SELECT DISTINCT {id_} FROM {table}")
        ids = sorted([x[0] for x in table_ids])
        
        num = [x for x in range(1, len(ids) + 1)]
        
        update_id = {}
        for x, y in zip(ids, num):
            if x != y:
                update_id[x] = y
        
        itm = sorted(update_id.items(), key=lambda x: x[0])
        
        for i in itm:
            self._conn.execute(f"UPDATE {table} SET {id_}={i[1]} WHERE {id_}={i[0]}")
    
    def _connect_to_db(self):
        # dialect+driver://username:password@host:port/database
        
        try:
            if self.dbms == "sqlite":
                engine = create_engine(f'sqlite:///{self.db_output}', echo=self.db_log)
            elif self.dbms == 'mysql':
                engine = create_engine(f'mysql+mysqlconnector://{self.db_username}:{self.db_password}@{self.host}:'
                                       f'{self.port}', echo=self.db_log)
            elif self.dbms == 'postgres':
                engine = create_engine(f'postgresql+psycopg2://{self.db_username}:{self.db_password}@{self.host}:'
                                       f'{self.port}', echo=self.db_log)
            else:
                raise NotImplementedError
            
            conn = engine.connect()
            
            self._engine = engine
            self._conn = conn
        except ProgrammingError as e:
            if 'Access denied' in str(e):
                logger.error(f"Access denied! Please check your password for {self.db_username}.")
            else:
                logger.error(str(e))
    
    def _close_the_db(self):
        self._conn.close()
    
    def _insert(self, object_, param):
        try:
            self._conn.execute(object_, param)
        except IntegrityError as e:
            logger.debug(f"Caught Integrity Error: {e}")
    
    def _set_repo_id(self):
        res = self._conn.execute(
            f"""
            SELECT repo_id
            FROM repository
            WHERE name='{self.repo_name}' AND owner='{self.repo_owner}'
            """
        ).fetchone()
        
        self.repo_id = res[0]
    
    def _get_user_id(self, login, user_object=None):
        if not login:
            assert user_object is not None
            
            res = self._conn.execute(
                f"""
                SELECT contributor_id
                FROM contributors
                WHERE login='{user_object.login}'
                """
            ).fetchone()
            
            if not res:
                self._dump_users(login=None, user_object=user_object)
                self._get_user_id(user_object.login)
            else:
                return res[0]
        else:
            res = self._conn.execute(
                f"""
                SELECT contributor_id
                FROM contributors
                WHERE login='{login}'
                """
            ).fetchone()
            
            if not res:
                self._dump_users(login=login)
                self._get_user_id(login)
            else:
                return res[0]
    
    def _get_table_id(self, table, field, value, pk='id'):
        res = self._conn.execute(
            f"""
            SELECT {pk}
            FROM {table}
            WHERE {field}='{value}' AND repo_id={self.repo_id}
            """
        ).fetchone()
        
        if not res:
            return None
        else:
            return res[0]
