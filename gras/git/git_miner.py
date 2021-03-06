import asyncio
import concurrent.futures
import logging
import multiprocessing as mp
import pickle
from collections import namedtuple
from datetime import datetime

from pygit2 import GIT_SORT_TIME, GIT_SORT_TOPOLOGICAL, Oid, Repository, Tag

from gras import ROOT
from gras.base_miner import BaseMiner
from gras.github.structs.contributor_struct import CommitUserStruct
from gras.github.structs.repository_struct import RepositoryStruct
from gras.utils import timing

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ModuleNotFoundError:
    pass

logger = logging.getLogger("main")
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

THREADS = min(32, mp.cpu_count() + 4)
MAX_INSERT_OBJECTS = 100
LOCKED = True
lock = mp.Lock()


class GitMiner(BaseMiner):
    Id_Name_Login = namedtuple("Id_Name_Login", ["id", "name", "login"])
    Code_Change = namedtuple("Code_Change", ["commit_id", "filename"])

    def __init__(self, args):
        super().__init__(args)

        self._initialise_db()

        if args.dbms == "sqlite":
            self._conn.execute("PRAGMA foreign_keys=ON")

        self.email_map = {}
        self.commit_id = {}
        self.id_commit = {}
        self.code_change_map = {}

        self.__init_user_emails()

        self._dump_repository()

        self.aio = args.aio

        if self.aio:
            self._create_loop()

        self.repo = Repository(args.path)
        self._fetch_references()
        self._dump_tags()
        self._fetch_commit_ids()

    def _create_loop(self):
        self.loop = asyncio.new_event_loop()

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def __init_user_emails(self):
        res = self.execute_query(
            """
            SELECT email, id, login, name
            FROM contributors
            WHERE email IS NOT NULL 
            """
        ).fetchall()

        for row in res:
            self.email_map[row[0]] = self.Id_Name_Login(id=row[1], name=row[2], login=row[3])

    def __init_code_change(self):
        res = self.execute_query(
            """
            SELECT id, commit_id, filename
            FROM code_change
            """
        ).fetchall()

        for row in res:
            self.code_change_map[self.Code_Change(commit_id=row[1], filename=row[2])] = row[0]

    def _dump_repository(self):
        logger.info("Dumping Repository...")

        res = self.execute_query(
            f"""
            SELECT repo_id 
            FROM repository
            WHERE name="{self.repo_name}" and owner="{self.repo_owner}"
            """
        ).fetchone()

        if res:
            self._set_repo_id(res[0])
        else:
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

    def _dump_tags(self):
        objects = []

        for tag in self.tags:
            ref = self.repo.lookup_reference(tag)
            tag_obj = self.repo[ref.target.hex]

            if isinstance(tag_obj, Tag):
                name = tag_obj.name
                msg = tag_obj.message
                tagged_object = tag_obj.hex
                tagger = self.__get_user_id(name=tag_obj.tagger.name, email=tag_obj.tagger.email, oid=tagged_object,
                                            is_author=False, is_tagger=True)
            else:
                name = tag.split('/')[-1]
                msg = tag_obj.message
                tagged_object = tag_obj.hex
                tagger = self.__get_user_id(name=tag_obj.author.name, email=tag_obj.author.email, oid=tagged_object,
                                            is_author=True, is_tagger=False)

            obj = self.db_schema.tags_object(
                name=name,
                tagged_object=tagged_object,
                message=msg,
                tagger=tagger
            )

            objects.append(obj)

        self._insert(object_=self.db_schema.tags.insert(), param=objects)

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

    def __init_commits(self, inverse=False):
        if not inverse:
            res = self.execute_query(
                f"""
                SELECT oid, id
                FROM commits
                WHERE repo_id={self.repo_id}
                """
            ).fetchall()

            for row in res:
                self.commit_id[row[0]] = row[1]
        else:
            res = self._conn.execute(
                f"""
                SELECT id, oid
                FROM commits
                WHERE repo_id={self.repo_id}
                """
            ).fetchall()

            for row in res:
                self.id_commit[row[0]] = row[1]

    def __get_commit_id(self, oid, pk=None):
        if not pk:
            try:
                return self.commit_id[oid]
            except KeyError:
                return None
        else:
            try:
                return self.id_commit[pk]
            except KeyError:
                self.__init_commits(inverse=True)
                res = self.__get_commit_id(oid=None, pk=pk)
                if not res:
                    raise Exception(f"GitMiner => __get_commit_id: Pk {pk} does not exist!")
                else:
                    return res

    def __check_user_id(self, email):
        try:
            map_ = self.email_map[email]
            return [map_.id, map_.login, map_.name]
        except KeyError:
            res = self.execute_query(
                f"""
                SELECT id, login, name
                FROM contributors
                WHERE email="{email}"
                """
            ).fetchone()

            if res:
                self.email_map[email] = self.Id_Name_Login(id=res[0], login=res[1], name=res[2])

            return res

    def __update_contributor(self, name, id_, login, email):
        name = name.replace('"', '""')

        self.execute_query(
            f"""
            UPDATE contributors
            SET name="{name}"
            WHERE id={id_}
            """
        )

        self.email_map[email] = self.Id_Name_Login(id=id_, login=login, name=name)

    def __get_user_id(self, name, email, oid, is_author, is_tagger):
        if not email:
            email = None

        if not name:
            name = None

        res = self.__check_user_id(email)

        if not res:
            user = CommitUserStruct(
                oid=oid,
                repo_name=self.repo_name,
                repo_owner=self.repo_owner,
                name=name,
                email=email,
                is_author=is_author,
                is_tagger=is_tagger
            ).process()

            if user is None:
                self._dump_anon_user_object(name=name, email=email, object_=self.db_schema.contributors.insert(),
                                            locked_insert=LOCKED)
            else:
                self._dump_user_object(login=None, user_object=user, object_=self.db_schema.contributors.insert(),
                                       locked_insert=LOCKED)

            return self.__get_user_id(name=name, email=email, oid=oid, is_author=is_author, is_tagger=is_tagger)
        else:
            if name == res[2]:
                return res[0]
            elif name == res[1]:
                return res[0]
            else:
                self.__update_contributor(name=name, id_=res[0], login=res[1], email=email)
                return res[0]

    def _dump_code_change(self, oid):
        commit = self.repo.get(oid)
        commit_id = self.__get_commit_id(oid)

        logger.debug(f"Dumping Code Change for commit_id -> {commit_id}...")

        code_change = []

        if commit:
            if not commit.parents:
                diffs = [self.repo.diff("4b825dc642cb6eb9a060e54bf8d69288fbee4904", commit)]
            else:
                diffs = [self.repo.diff(i, commit) for i in commit.parents]

            total_diffs = len(diffs)
            for diff in diffs:
                logger.debug(f"Remaining: {total_diffs}")
                total_diffs -= 1
                for patch in diff:
                    obj = self.db_schema.code_change_object(
                        repo_id=self.repo_id,
                        commit_id=commit_id,
                        filename=patch.delta.new_file.path,
                        additions=patch.line_stats[1],
                        deletions=patch.line_stats[2],
                        changes=patch.line_stats[1] + patch.line_stats[2],
                        change_type=self.__get_status(patch.delta.status)
                    )

                    code_change.append(obj)

            self._insert(object_=self.db_schema.code_change.insert(), param=code_change)
            logger.debug(f"Successfully dumped code change for {oid}!")

    def __get_code_change_id(self, commit_id, filename):
        try:
            return self.code_change_map[self.Code_Change(commit_id=commit_id, filename=filename)]
        except KeyError:
            return Exception(f"GitMiner => __get_code_change_id: Object does not exist! commit_id={commit_id}, "
                             f"filename:{filename}")

    def _dump_patches(self, oid):
        commit = self.repo.get(oid)
        commit_id = self.__get_commit_id(oid)

        logger.debug(f"Dumping Patch for commit_id -> {commit_id}...")

        patches = []

        if not commit.parents:
            diffs = [self.repo.diff("4b825dc642cb6eb9a060e54bf8d69288fbee4904", commit)]
        else:
            diffs = [self.repo.diff(i, commit) for i in commit.parents]

        total_diffs = len(diffs)
        for diff in diffs:
            logger.debug(f"Remaining: {total_diffs}")
            total_diffs -= 1
            for patch in diff:
                obj = self.db_schema.patches_object(
                    code_change_id=self.__get_code_change_id(commit_id, patch.delta.new_file.path),
                    patch=patch.patch
                )

                patches.append(obj)

        self._insert(object_=self.db_schema.patches.insert(), param=patches)
        logger.debug(f"Successfully dumped patch for {oid}!")

    def _dump_commit(self, oid):
        logger.debug(f"Inserting for commit: {oid}...")
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
        author_id = self.__get_user_id(name=author_name, email=author_email, oid=oid.hex, is_author=True,
                                       is_tagger=False) if \
            author_email.strip() else None
        authored_date = datetime.fromtimestamp(commit.author.time)

        committer_name = commit.committer.name
        committer_email = commit.committer.email

        if committer_email == "noreply@github.com":
            committer_id = author_id
        else:
            committer_id = self.__get_user_id(name=committer_name, email=committer_email, oid=oid.hex,
                                              is_author=False, is_tagger=False) if committer_email.strip() else None

        committed_date = datetime.fromtimestamp(commit.commit_time)

        message = commit.message

        if len(commit.parents) > 1:
            is_merge = 1
        else:
            is_merge = 0

        obj = self.db_schema.commits_object(
            repo_id=self.repo_id,
            oid=oid.hex,
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

        self._insert(object_=self.db_schema.commits.insert(), param=obj)
        logger.debug(f"Successfully dumped commit: {oid.hex}")

    def __fetch_branch_commits(self, branch_target):
        logger.info(f"Ongoing Branch {branch_target[0]}...")

        for commit in self.repo.walk(branch_target[1], GIT_SORT_TOPOLOGICAL | GIT_SORT_TIME):
            if commit.oid not in self.commits:
                self.commits.add(commit.oid)
            else:
                break

    def _fetch_commit_ids(self):
        try:
            with open(f"{ROOT}/.gras-cache/{self.repo_name}_commits.txt", "rb") as fp:
                self.commits = pickle.load(fp)

            self.commits = [Oid(hex=x) for x in self.commits]

            logger.info(f"TOTAL COMMITS: {len(self.commits)}")
            return self.commits
        except FileNotFoundError:
            logger.error("Commits file not present, dumping...")

        self.commits = set()
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            process = {executor.submit(self.__fetch_branch_commits, branch_target): branch_target for branch_target
                       in self.branches.items()}

            for future in concurrent.futures.as_completed(process):
                branch_target = process[future]
                logger.info(f"Fetched for {branch_target[0]}, Total: {len(self.commits)}")

        logger.info(f"TOTAL COMMITS: {len(self.commits)}")
        with open(f"{ROOT}/.gras-cache/{self.repo_name}_commits.txt", "wb") as fp:
            temp = [x.hex for x in self.commits]
            pickle.dump(temp, fp)
            del temp

    @timing(name="commits", is_stage=True)
    def _parse_commits(self):
        res = self.execute_query(
            f"""
            SELECT DISTINCT oid
            FROM commits
            """
        ).fetchall()

        dumped_commits = [x[0] for x in res]
        del res

        commits = list(self.commits)
        for i in range(0, len(commits), THREADS):
            proc = [mp.Process(target=self._dump_commit, args=(oid,)) for oid in commits[i:i + THREADS] if
                    oid.hex not in dumped_commits]
            for p in proc:
                p.start()

            while any([p.is_alive() for p in proc]):
                continue

    @timing(name="code change", is_stage=True)
    def _parse_code_change(self):
        id_oid = self.execute_query(
            f"""
            SELECT id, oid
            FROM commits
            """
        ).fetchall()

        dumped_ids = self.execute_query(
            f"""
            SELECT DISTINCT commit_id
            FROM code_change       
            """
        ).fetchall()

        dumped_ids = [x[0] for x in dumped_ids]

        not_dumped_commits = [x[1] for x in id_oid if x[0] not in dumped_ids]
        del dumped_ids
        del id_oid

        for i in range(0, len(not_dumped_commits), THREADS):
            proc = [mp.Process(target=self._dump_code_change, args=(oid,)) for oid in
                    not_dumped_commits[i: i + THREADS]]
            for p in proc:
                p.start()

            while any([x.is_alive() for x in proc]):
                continue

    @timing(name="patches", is_stage=True)
    def _parse_patches(self):
        self.__init_commits(inverse=True)

        res = self.execute_query(
            f"""
            SELECT id, commit_id
            FROM code_change
            """
        ).fetchall()

        cc_commit = {}
        for row in res:
            cc_commit[row[0]] = row[1]

        res = self.execute_query(
            """
            SELECT code_change_id
            FROM patches
            """
        )

        not_dumped_commits = set(cc_commit.values()).difference({cc_commit[x[0]] for x in res})
        not_dumped_commits = sorted([self.id_commit[id_] for id_ in not_dumped_commits])

        del cc_commit

        for i in range(0, len(not_dumped_commits), THREADS):
            proc = [mp.Process(target=self._dump_code_change, args=(oid,)) for oid in
                    not_dumped_commits[i: i + THREADS]]
            for p in proc:
                p.start()

            while any([x.is_alive() for x in proc]):
                continue

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
            self.__init_commits()
            self._parse_code_change()

        # self._parse_patches()

    def __del__(self):
        if self.aio:
            self.loop.close()
