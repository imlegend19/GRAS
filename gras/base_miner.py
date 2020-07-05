import concurrent.futures
import logging
import os
import signal
from abc import ABCMeta, abstractmethod
from collections import namedtuple

from neo4j import GraphDatabase
from neo4j._exceptions import BoltError
from neo4j.exceptions import ServiceUnavailable
from sqlalchemy import create_engine
from sqlalchemy.engine import ResultProxy
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

from gras.db.db_models import DBSchema
from gras.errors import DatabaseError, GithubMinerError, InvalidTokenError
from gras.github.structs.contributor_struct import UserStruct, UserStructV3
from gras.github.structs.rate_limit import RateLimitStruct
from gras.utils import locked, to_iso_format

logger = logging.getLogger("main")


class BaseMiner(metaclass=ABCMeta):
    """
    BaseMiner class to store parameters parsed by `ArgumentParse` and start the mining process
    """
    Name_Email = namedtuple("Name_Email", ["name", "email"])

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

        self.login_id = {}
        self.name_email_id = {}

        self.animator = args.animator
        self.tokens = args.tokens
        self.chunk_size = args.chunk_size

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    @abstractmethod
    def load_from_file(self, **kwargs):
        pass

    @abstractmethod
    def dump_to_file(self, **kwargs):
        pass

    @abstractmethod
    def process(self):
        pass

    def _connect_to_engine(self):
        self._engine, self._conn = self.engine, self.engine.connect()
        self.db_schema = DBSchema(conn=self._conn, engine=self._engine)
        self.db_schema.create_tables()

    def _initialise_db(self):
        # dialect+driver://username:password@db_host:db_port/database

        try:
            if self.dbms == "sqlite":
                self.engine = create_engine(
                    f'sqlite:///{self.db_output}', echo=self.db_log, pool_pre_ping=True,
                    connect_args={
                        'check_same_thread': False
                    })
                self._connect_to_engine()
            elif self.dbms == 'mysql':
                self.engine = create_engine(
                    f'mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}:'
                    f'{self.db_port}/{self.db_name}?charset=utf8mb4', echo=self.db_log, pool_pre_ping=True,
                    connect_args={
                        'check_same_thread': False
                    })
                self._connect_to_engine()
            elif self.dbms == 'postgresql':
                self.engine = create_engine(
                    f'postgresql+psycopg2://{self.db_username}:{self.db_password}@{self.db_host}:'
                    f'{self.db_port}/{self.db_name}', echo=self.db_log, pool_pre_ping=True,
                    connect_args={
                        'check_same_thread': False
                    })
                self._connect_to_engine()
            elif self.dbms == 'neo4j':
                self.engine = None

                try:
                    self._conn = GraphDatabase.driver(
                        uri=f"bolt://{self.db_host}:{self.db_port}", auth=(self.db_username, self.db_password)
                    )
                except ServiceUnavailable as e:
                    logger.error("Failed to establish connection to the database!")
                    raise DatabaseError(msg=e)
                except BoltError:
                    try:
                        self._conn = GraphDatabase.driver(
                            uri=f"bolt://{self.db_host}:{self.db_port}", auth=(self.db_username, self.db_password),
                            encrypted=False
                        )
                    except Exception as e:
                        raise DatabaseError(msg=e)
            else:
                raise NotImplementedError
        except ProgrammingError as e:
            if 'Access denied' in str(e):
                logger.error(f"Access denied! Please check your password for {self.db_username}.")
            else:
                logger.error(str(e))
        except Exception as e:
            logger.error("Failed to establish connection to the database!")
            raise DatabaseError(msg=e)

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

        table_ids: ResultProxy = self._conn.execute(f"SELECT DISTINCT {id_} FROM {table}")

        ids = sorted([x[0] for x in table_ids])

        num = [x for x in range(1, len(ids) + 1)]

        update_id = {}
        for x, y in zip(ids, num):
            if x != y:
                update_id[x] = y

        itm = sorted(update_id.items(), key=lambda x: x[0])

        # for i in itm:
        #     self._conn.execute(f"UPDATE {table} SET {id_}={i[1]} WHERE {id_}={i[0]}")

    @locked
    def _insert(self, object_, param, tries=1):
        cnt = 0

        try:
            if param:
                inserted = self._conn.execute(object_, param)
                cnt = inserted.rowcount
                logger.debug(f"Try 1: Affected Rows = {cnt}")
        except IntegrityError as e:
            logger.debug(f"Caught Integrity Error: {e}")
        except OperationalError as e:
            if tries > 3:
                logger.error(f"Maximum tries exceeded. Cannot connect to database. Error: {e}")
                os._exit(1)
            logger.debug(f"Caught Operational Error! Try: {tries + 1}")
            self._initialise_db()
            self._insert(object_, param, tries + 1)
        except Exception as e:
            logger.error(f"_insert(): {e}")

        return cnt

    def _serial_insert(self, object_, param, tries=1):
        try:
            if param:
                inserted = self._conn.execute(object_, param)
                logger.debug(f"Affected Rows: {inserted.rowcount}")
        except IntegrityError as e:
            logger.debug(f"Caught Integrity Error: {e}")
        except OperationalError as e:
            if tries > 3:
                logger.error(f"Maximum tries exceeded. Cannot connect to database. Error: {e}")
                os._exit(1)
            logger.debug(f"Caught Operational Error! Try: {tries + 1}")
            self._connect_to_engine()
            self._insert(object_, param, tries + 1)
        except Exception as e:
            raise e

    @locked
    def execute_query(self, query, tries=1):
        try:
            res = self._conn.execute(query)
        except OperationalError as e:
            if tries > 3:
                logger.error(f"Maximum tries exceeded. Cannot connect to database. Error: {e}")
                os._exit(1)
            logger.debug(f"Caught Operational Error! Try: {tries + 1}")
            self._connect_to_engine()
            res = self.execute_query(query, tries + 1)
        except Exception as e:
            raise e

        return res

    def _set_repo_id(self, id_=None):
        if not id_:
            res = self._conn.execute(
                f"""
                SELECT repo_id
                FROM repository
                WHERE name="{self.repo_name}" AND owner="{self.repo_owner}"
                """
            ).fetchone()

            self.repo_id = res[0]
        else:
            self.repo_id = id_

    def _close_the_db(self):
        self._conn.close()

    @staticmethod
    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    @locked
    def __add_user_to_cache(self, login, name=None, email=None):
        if login:
            res = self._conn.execute(
                f"""
                SELECT id
                FROM contributors
                WHERE login="{login}"
                """
            ).fetchone()

            self.login_id[login] = res[0]
        else:
            res = self._conn.execute(
                f"""
                SELECT id
                FROM contributors
                WHERE name="{name}" AND email="{email}"
                """
            ).fetchone()

            if res:
                self.name_email_id[self.Name_Email(name=name, email=email)] = res[0]

    def _dump_anon_user_object(self, name, email, object_, locked_insert=True):
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

        if locked_insert:
            self._insert(object_, obj)
        else:
            self._serial_insert(object_, obj)

        self.__add_user_to_cache(login=None, name=name, email=email)

        return True

    def _dump_user_object(self, login, object_, user_object=None, locked_insert=True):
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
                except Exception:
                    # User may be a bot
                    try:
                        user = UserStructV3(
                            login=login + "[bot]",
                            is_bot=True
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

            logger.debug(f"Dumping User with login: {login}")

            if locked_insert:
                self._insert(object_, obj)
            else:
                self._serial_insert(object_, obj)

            self.__add_user_to_cache(login=login)
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
            if locked_insert:
                self._insert(object_, obj)
            else:
                self._serial_insert(object_, obj)

            self.__add_user_to_cache(login=user_object.login)
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
