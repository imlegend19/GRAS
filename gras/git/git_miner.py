import asyncio
import concurrent.futures
import logging
import multiprocessing as mp
from datetime import datetime

from pygit2 import GIT_SORT_TIME, GIT_SORT_TOPOLOGICAL, Repository

from gras.base_miner import BaseMiner
from gras.db.db_models import DBSchema
from gras.github.structs.contributor_struct import CommitUserStruct
from gras.github.structs.repository_struct import RepositoryStruct
from gras.utils import locked, timing

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ModuleNotFoundError:
    pass

logger = logging.getLogger("main")
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

THREADS = min(32, mp.cpu_count() + 4)
MAX_INSERT_OBJECTS = 100


class GitMiner(BaseMiner):
    def __init__(self, args):
        super().__init__(args)

        self._engine, self._conn = self._connect_to_db()
        self.db_schema = DBSchema(conn=self._conn, engine=self._engine)

        self.db_schema.create_tables()
        self._dump_repository()

        self.aio = args.aio

        if self.aio:
            self._create_loop()

        self.repo = Repository(args.path)
        self._fetch_references()
        self.commits = self._fetch_commit_ids()

    def _create_loop(self):
        self.loop = asyncio.new_event_loop()

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def _dump_repository(self):
        logger.info("Dumping Repository...")

        repo = RepositoryStruct(
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
        self._set_repo_id()

    def _fetch_references(self):
        self.tags, self.branches = [], {}
        for reference in self.repo.listall_references():
            if 'refs/tags' in reference:
                self.tags.append(reference)
            else:
                self.branches[reference] = self.repo.lookup_reference(reference).peel().oid

    @staticmethod
    def __get_status(status):
        if status == 1:
            return 'ADDED'
        elif status == 2:
            return 'DELETED'
        elif status == 3:
            return 'MODIFIED'
        elif status == 4:
            return 'RENAMED'
        elif status == 5:
            return 'COPIED'
        elif status == 6:
            return 'IGNORED'
        elif status == 7:
            return 'UNTRACKED'
        elif status == 8:
            return 'TYPECHANGED'
        else:
            return None

    @locked
    def __get_commit_id(self, oid):
        res = self._conn.execute(
            f"""
            SELECT id
            FROM commits
            WHERE oid="{oid}" AND repo_id={self.repo_id}
            """
        ).fetchone()

        return res[0]

    @locked
    def __check_user_id(self, email):
        res = self._conn.execute(
            f"""
            SELECT id, login, name
            FROM contributors
            WHERE email="{email}"
            """
        ).fetchone()

        return res

    @locked
    def __update_contributor(self, name, id_):
        name = name.replace('"', '""')

        self._conn.execute(
            f"""
            UPDATE contributors
            SET name="{name}"
            WHERE id={id_}
            """
        )

    def __get_user_id(self, name, email, oid, is_author):
        res = self.__check_user_id(email)

        if not res:
            user = CommitUserStruct(
                oid=oid,
                repo_name=self.repo_name,
                repo_owner=self.repo_owner,
                name=name,
                email=email,
                is_author=is_author
            ).process()

            if user is None:
                self._dump_anon_user_object(name=name, email=email, object_=self.db_schema.contributors.insert())
            else:
                self._dump_user_object(login=None, user_object=user, object_=self.db_schema.contributors.insert())

            return self.__get_user_id(name=name, email=email, oid=oid, is_author=is_author)
        else:
            if name == res[2]:
                return res[0]
            elif name == res[1]:
                return res[0]
            else:
                self.__update_contributor(name, res[0])
                return res[0]

    def _dump_code_change(self, oid):
        commit = self.repo.get(oid)
        commit_id = self.__get_commit_id(oid)

        logger.debug(f"Dumping Code Change for commit_id -> {commit_id}...")

        code_change = []

        if not commit.parents:
            diffs = [self.repo.diff("4b825dc642cb6eb9a060e54bf8d69288fbee4904", commit)]
        else:
            diffs = [self.repo.diff(i, commit) for i in commit.parents]

        total_diffs = len(diffs)
        for diff in diffs:
            print(f"Remaining: {total_diffs}")
            total_diffs -= 1
            for patch in diff:
                obj = self.db_schema.code_change_object(
                    repo_id=self.repo_id,
                    commit_id=commit_id,
                    filename=patch.delta.new_file.path,
                    additions=patch.line_stats[1],
                    deletions=patch.line_stats[2],
                    changes=patch.line_stats[1] + patch.line_stats[2],
                    change_type=self.__get_status(patch.delta.status),
                    patch=patch.patch
                )

                code_change.append(obj)

        logger.debug(f"Inserting for {oid}...")
        self._insert(object_=self.db_schema.code_change.insert(), param=code_change)
        logger.debug("Inserted!")

        return oid

    def _dump_commit(self, oid):
        commit = self.repo.get(oid)

        if not commit.parents:
            diffs = [self.repo.diff("4b825dc642cb6eb9a060e54bf8d69288fbee4904", commit)]
        else:
            diffs = [self.repo.diff(i, commit) for i in commit.parents]

        num_files_changed = 0
        additions, deletions = 0, 0
        for diff in diffs:
            num_files_changed += diff.stats.files_changed
            additions += diff.stats.insertions
            deletions += diff.stats.deletions

        author_name = commit.author.name
        author_email = commit.author.email
        author_id = self.__get_user_id(name=author_name, email=author_email, oid=oid, is_author=True)
        authored_date = datetime.fromtimestamp(commit.author.time)

        committer_name = commit.committer.name
        committer_email = commit.committer.email

        if committer_email == "noreply@github.com":
            committer_id = author_id
        else:
            committer_id = self.__get_user_id(name=committer_name, email=committer_email, oid=oid, is_author=False)

        committed_date = datetime.fromtimestamp(commit.commit_time)

        message = commit.message

        if len(commit.parents) > 1:
            is_merge = 1
        else:
            is_merge = 0

        obj = self.db_schema.commits_object(
            repo_id=self.repo_id,
            oid=str(oid),
            additions=additions,
            deletions=deletions,
            author_id=author_id,
            authored_date=authored_date,
            committer_id=committer_id,
            committer_date=committed_date,
            message=message,
            num_files_changed=num_files_changed,
            is_merge=is_merge
        )

        logger.debug(f"Inserting for {oid}...")
        self._insert(object_=self.db_schema.commits.insert(), param=obj)
        logger.debug("Inserted!")

        return oid

    def _fetch_commit_ids(self):
        commits = list()
        for branch, target in self.branches.items():
            logger.info(f"Ongoing Branch {branch}...")

            for commit in self.repo.walk(target, GIT_SORT_TOPOLOGICAL | GIT_SORT_TIME):
                if commit.oid not in commits:
                    commits.append(commit.oid)
                else:
                    break

        logger.info(f"TOTAL COMMITS: {len(commits)}")
        return commits

    @timing(name="commits", is_stage=True)
    def _parse_commits(self):
        res = self._conn.execute(
            f"""
            SELECT DISTINCT oid
            FROM commits
            """
        ).fetchall()

        dumped_commits = [x[0] for x in res]
        del res

        index = 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            process = {executor.submit(self._dump_commit, oid): oid for oid in self.commits if
                       oid.hex not in dumped_commits}
            for future in concurrent.futures.as_completed(process):
                oid = process[future]
                logger.info(f"Dumped commit: {oid}, index: {index}")
                index += 1

    @timing(name="code change", is_stage=True)
    def _parse_code_change(self):
        res = self._conn.execute(
            f"""
            SELECT oid 
            FROM commits
            WHERE id in (
                SELECT DISTINCT commit_id
                FROM code_change 
            )           
            """
        )

        dumped_commits = [x[0] for x in res]
        del res

        index = 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            process = {executor.submit(self._dump_code_change, oid): oid for oid in self.commits if
                       oid.hex not in dumped_commits}
            for future in concurrent.futures.as_completed(process):
                oid = process[future]
                logger.info(f"Dumped Code Change for commit: {oid}, index: {index}")
                index += 1

    @timing(name="async -> commits", is_stage=True)
    async def _async_parse_commits(self):
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(self.executor, self._dump_commit, oid) for oid in self.commits]
        completed, _ = await asyncio.wait(tasks)
        for t in completed:
            logger.info(f"Dumped commit: {t.result()}")

    @timing(name="async -> code change", is_stage=True)
    async def _async_parse_code_change(self):
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(self.executor, self._dump_code_change, oid) for oid in self.commits]
        completed, _ = await asyncio.wait(tasks)
        for t in completed:
            logger.info(f"Dumped Code Change for commit: {t.result()}")

    def process(self):
        if self.aio:
            self.loop.run_until_complete(self._parse_commits())
            self.loop.run_until_complete(self._parse_code_change())
        else:
            # self._parse_commits()
            self._parse_code_change()

    def __del__(self):
        if self.aio:
            self.loop.close()
