import concurrent.futures
import logging
import signal
from abc import ABCMeta, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, ProgrammingError

from gras.errors import GithubMinerError, InvalidTokenError
from gras.github.structs.contributor_struct import UserStruct, UserStructV3
from gras.github.structs.rate_limit import RateLimitStruct
from gras.utils import locked, to_iso_format

logger = logging.getLogger("main")


class BaseMiner(metaclass=ABCMeta):
    """
    BaseMiner class to store parameters parsed by `ArgumentParse` and start the mining process
    """

    def __init__(self, args):
        self.interface = args.interface
        self.repo_owner = args.repo_owner
        self.repo_name = args.repo_name
        self.start_date = to_iso_format(args.start_date)
        self.end_date = to_iso_format(args.end_date)
        self.full = args.full

        self.basic = args.basic
        self.basic_extra = args.basic_extra
        self.issue_tracker = args.issue_tracker
        self.commit = args.commit
        self.pull_tracker = args.pull_tracker

        self.dbms = args.dbms
        self.db_name = args.db_name
        self.db_username = args.db_username
        self.db_password = args.db_password
        self.db_output = args.db_output
        self.db_host = args.db_host
        self.db_port = args.db_port
        self.db_log = args.db_log

        self.animator = args.animator
        self.tokens = args.tokens
        self.chunk_size = args.chunk_size

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    @abstractmethod
    def load_from_file(self, **kwargs):
        """
        :func: `abc.abstractmethod` to load the settings from a .cfg file and instantiate the
        :class:`gras.base_miner.BaseMiner` class.
        
        Args:
            file: The .cfg file where the settings are stored

        Returns:
            None
        """
        pass

    @abstractmethod
    def dump_to_file(self, **kwargs):
        """
        Method to dump the :class:`gras.base_miner.BaseMiner` object to a .cfg (config) file
        
        Args:
            path: The path of the .cfg file to be dumped

        Returns:
            None

        """
        pass

    @abstractmethod
    def process(self):
        pass

    def _connect_to_db(self):
        # dialect+driver://username:password@db_host:db_port/database

        try:
            if self.dbms == "sqlite":
                engine = create_engine(
                    f'sqlite:///{self.db_output}', echo=self.db_log, pool_pre_ping=True,
                    connect_args={
                        'check_same_thread': False
                    })
            elif self.dbms == 'mysql':
                engine = create_engine(
                    f'mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}:'
                    f'{self.db_port}/{self.db_name}?charset=utf8mb4', echo=self.db_log, pool_pre_ping=True,
                    connect_args={
                        'check_same_thread': False
                    })
            elif self.dbms == 'postgresql':
                engine = create_engine(
                    f'postgresql+psycopg2://{self.db_username}:{self.db_password}@{self.db_host}:'
                    f'{self.db_port}/{self.db_name}', echo=self.db_log, pool_pre_ping=True,
                    connect_args={
                        'check_same_thread': False
                    })
            else:
                raise NotImplementedError

            return engine, engine.connect()
        except ProgrammingError as e:
            if 'Access denied' in str(e):
                logger.error(f"Access denied! Please check your password for {self.db_username}.")
            else:
                logger.error(str(e))

    @staticmethod
    def __get_not_null_clause(clause):
        clause_list = []

        for field in clause.split(','):
            clause_list.append(f"{field} IS NOT NULL")

        return " AND".join(clause_list)

    def _refactor_table(self, id_, table, group_by):
        logger.info(f"Refactoring Table: {table}")

        deleted = self._conn.execute(
            f"""
            DELETE FROM {table}
            WHERE {id_} IN (
                SELECT max({id_})
                FROM {table}
                WHERE {self.__get_not_null_clause(group_by)}
                GROUP BY {group_by}
                HAVING COUNT(*) > 1
            )
            """
        )

        logger.debug(f"Affected Rows: {deleted.rowcount}")
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

    @locked
    def _insert(self, object_, param):
        try:
            if param:
                inserted = self._conn.execute(object_, param)
                logger.debug(f"Affected Rows: {inserted.rowcount}")
        except IntegrityError as e:
            logger.debug(f"Caught Integrity Error: {e}")
            pass

    def _set_repo_id(self):
        res = self._conn.execute(
            f"""
            SELECT repo_id
            FROM repository
            WHERE name="{self.repo_name}" AND owner="{self.repo_owner}"
            """
        ).fetchone()

        self.repo_id = res[0]

    def _close_the_db(self):
        self._conn.close()

    @staticmethod
    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def _dump_anon_user_object(self, name, email, object_):
        logger.info(f"Dumping anonymous user (name: {name}, email: {email})...")

        obj = self.db_schema.contributors_object(
            user_type="USER",
            login=None,
            name=name,
            email=email,
            created_at=None,
            updated_at=None,
            total_followers=0,
            location=None,
            is_anonymous=1
        )

        self._insert(object_, obj)

        return True

    def _dump_user_object(self, login, object_, user_object=None):
        if login:
            try:
                user = UserStruct(
                    login=login
                ).process()
            except Exception:
                try:
                    user = UserStructV3(
                        login=login
                    ).process()
                except Exception as e:
                    logger.error(e)
                    return False

                if not user:
                    return False

            if not user:
                user = UserStructV3(
                    login=login
                ).process()

                if not user:
                    return False

            obj = self.db_schema.contributors_object(
                user_type=user.user_type,
                login=login,
                name=user.name,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
                total_followers=user.total_followers,
                location=user.location,
                is_anonymous=0
            )

            # logger.debug(f"Dumping User with login: {login}")
            self._insert(object_, obj)
        elif user_object:
            obj = self.db_schema.contributors_object(
                user_type=user_object.user_type,
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
            self._insert(object_, obj)
        else:
            raise GithubMinerError(msg="`_dump_users()` exception! Please consider reporting this error to the team.")

        return True

    @staticmethod
    def __get_rate_limit(token):
        rate = RateLimitStruct(
            github_token=token
        ).process()

        return rate.remaining

    def get_next_token(self):
        rem_token = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            process = {executor.submit(self.__get_rate_limit, token): token for token in self.tokens}
            for future in concurrent.futures.as_completed(process):
                token = process[future]

                try:
                    remaining = future.result()
                except Exception as e:
                    raise InvalidTokenError(msg=str(e))

                rem_token.append((remaining, token))

        rem_token.sort(reverse=True, key=lambda x: x[0])
        return rem_token[0][1]
