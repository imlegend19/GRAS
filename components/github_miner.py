import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, ProgrammingError

from components.base_miner import BaseMiner
from components.db.models import DBSchema
from components.query_engine.entity.github_models import AnonContributorModel
from components.query_engine.structs.contributor_struct import ContributorList, UserNodesStruct
from components.query_engine.structs.repository_struct import RepositoryStruct

logger = logging.getLogger("main")


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
        # self._dump_users(node_ids=node_ids)
        self._dump_repository()
        
        # self._refactor_contributors()
        # self._reorder_table("contributor_id", "contributors")
        
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
        
        logger.debug("Dumping anonymous contributors...")
        self._insert(self.db_schema.contributors.insert(), obj_list)
        
        return node_ids
    
    def _dump_users(self, node_ids=None, *args):
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
                
                logger.debug("Dumping other contributors...")
                self._insert(self.db_schema.contributors.insert(), obj_list)
        elif args:
            raise NotImplementedError
        else:
            raise NotImplementedError
    
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
        
        self._insert(self.db_schema.repository.insert(), obj)
    
    def _refactor_contributors(self):
        self._conn.execute(
            """
            DELETE FROM contributors
            WHERE contributor_id IN (
                SELECT max(contributor_id) FROM contributors
                GROUP BY login, name, email
                HAVING count(*) > 1
            )
            """
        )
    
    def _reorder_table(self, id_, table):
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
        except IntegrityError:
            pass
