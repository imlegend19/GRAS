import concurrent.futures
import logging
import multiprocessing as mp
from datetime import datetime

from pygit2 import GIT_SORT_TIME, GIT_SORT_TOPOLOGICAL, Repository

from gras.base_miner import BaseMiner
from gras.db.db_models import DBSchema
from gras.github.structs.contributor_struct import CommitUserStruct
from gras.utils import timing

logger = logging.getLogger("main")
THREADS = min(32, mp.cpu_count() + 4)
MAX_INSERT_OBJECTS = 1000


class GitMiner(BaseMiner):
    COMMITS = []
    CODE_CHANGE = []
    
    def __init__(self, args):
        super().__init__(args)
        
        self._engine, self._conn = self._connect_to_db()
        self.db_schema = DBSchema(conn=self._conn, engine=self._engine)
        self._set_repo_id()
        
        self.db_schema.create_tables()
        
        self.repo = Repository(args.path)
        self._fetch_references()
        self.process()
    
    def _load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass
    
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
    
    def __get_commit_id(self, oid):
        res = self._conn.execute(
            f"""
            SELECT id
            FROM commits
            WHERE oid="{oid}" AND repo_id={self.repo_id}
            """
        ).fetchone()
        
        return res[0]
    
    def __get_user_id(self, name, email, oid):
        res = self._conn.execute(
            f"""
            SELECT id, login, name
            FROM contributors
            WHERE email="{email}"
            """
        ).fetchone()
        
        if not res:
            user = CommitUserStruct(
                oid=oid,
                repo_name=self.repo_name,
                repo_owner=self.repo_owner,
                name=name,
                email=email
            ).process()
            
            if user is None:
                self._dump_anon_user_object(name=name, email=email, object_=self.db_schema.contributors.insert())
            else:
                self._dump_user_object(login=None, user_object=user, object_=self.db_schema.contributors.insert())
            
            return self.__get_user_id(name=name, email=email, oid=oid)
        else:
            if name == res[2]:
                return res[0]
            elif name == res[1]:
                return res[0]
            else:
                self._conn.execute(
                    f"""
                    UPDATE contributors
                    SET name="{name}"
                    WHERE id={res[0]}
                    """
                )
                
                return res[0]
    
    def _dump_code_change(self, oid):
        commit = self.repo.get(oid)
        commit_id = self.__get_commit_id(oid)
        
        logger.debug(f"Dumping Code Change for commit_id -> {commit_id}...")
        
        code_change = []
        
        if not commit.parents:
            diffs = [self.repo.diff("4b825dc642cb6eb9a060e54bf8d69288fbee4904", commit)]
        else:
            diffs = [self.repo.diff(commit.parents[i], commit) for i in commit.parents]
        
        for diff in diffs:
            for patch in diff:
                obj = self.db_schema.code_change_object(
                    repo_id=self.repo_id,
                    commit_id=commit_id,
                    filename=patch.delta.new_file.path,
                    additions=patch.line_stats[1],
                    deletions=patch.line_stats[2],
                    changes=patch.line_stats[1] + patch.line_stats[2],
                    change_type=self.__get_status(patch.status),
                    patch=patch.patch
                )

                code_change.append(obj)

        self.CODE_CHANGE.extend(code_change)

        if len(self.CODE_CHANGE) == 1000:
            logger.info("Inserting 1000 code changes...")
            self._insert(object_=self.db_schema.code_change.insert(), param=self.CODE_CHANGE)
            logger.info("Success!")
            self.CODE_CHANGE.clear()
    
    def _dump_commit(self, oid):
        commit = self.repo.get(oid)
        
        diff = self.repo.diff(commit.parents[0], commit)
        num_files_changed = diff.stats.files_changed
        additions = diff.stats.insertions
        deletions = diff.stats.deletions
        
        author_name = commit.author.name
        author_email = commit.author.email
        author_id = self.__get_user_id(name=author_name, email=author_email, oid=oid)
        authored_date = datetime.fromtimestamp(commit.author.time)
        
        committer_name = commit.committer.name
        committer_email = commit.committer.email
        
        if committer_email == "noreply@github.com":
            committer_id = author_id
        else:
            committer_id = self.__get_user_id(name=committer_name, email=committer_email, oid=oid)
        
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

        self.COMMITS.append(obj)

        if len(self.COMMITS) == 1000:
            logger.info("Inserting 1000 commits...")
            self._insert(object_=self.db_schema.commits.insert(), param=self.COMMITS)
            logger.info("Success!")
            self.COMMITS.clear()
    
    def _fetch_commit_ids(self):
        commits = list()
        for branch, target in self.branches.items():
            logger.info(f"Ongoing Branch {branch}...")
            
            for commit in self.repo.walk(target, GIT_SORT_TOPOLOGICAL | GIT_SORT_TIME):
                if commit.oid not in commits:
                    commits.append(commit.oid)
                else:
                    break
        
        return commits
    
    @timing(name="commits", is_stage=True)
    def _dump_commits(self, commits):
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            process = {executor.submit(self._dump_commit, oid): oid for oid in commits}
            for future in concurrent.futures.as_completed(process):
                oid = process[future]
                logger.info(f"Dumped commit: {oid}")
    
        self._insert(object_=self.db_schema.commits.insert(), param=self.COMMITS)
        del self.COMMITS
    
    @timing(name="code change", is_stage=True)
    def _dump_code_change(self, commits):
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            process = {executor.submit(self._dump_code_change, oid): oid for oid in commits}
            for future in concurrent.futures.as_completed(process):
                oid = process[future]
                logger.info(f"Dumped Code Change for commit: {oid}")
    
        self._insert(object_=self.db_schema.code_change.insert(), param=self.CODE_CHANGE)
        del self.CODE_CHANGE
    
    def process(self):
        commits = self._fetch_commit_ids()
        
        for oid in commits:
            self._dump_commit(oid)
        
        self._dump_commits(commits)
        self._dump_code_change(commits)
