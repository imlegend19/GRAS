import logging
import multiprocessing as mp
import signal

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, ProgrammingError

from gras.base_miner import BaseMiner
from gras.db.models import DBSchema
from gras.errors import GithubMinerError
from gras.github.entity.github_models import AnonContributorModel
from gras.github.structs.branch_struct import BranchStruct
from gras.github.structs.comment_struct import CommentStruct
from gras.github.structs.commit_comment_struct import CommitCommentStruct
from gras.github.structs.commit_struct import CodeChangeStruct, CommitStructV4
from gras.github.structs.contributor_struct import (
    ContributorList, UserNodesStruct, UserStruct,
    UserStructV3
)
from gras.github.structs.event_struct import EventStruct
from gras.github.structs.fork_struct import ForkStruct
from gras.github.structs.issue_struct import IssueStruct
from gras.github.structs.label_struct import LabelStruct
from gras.github.structs.language_struct import LanguageStruct
from gras.github.structs.milestone_struct import MilestoneStruct
from gras.github.structs.pull_struct import PullRequestStruct
from gras.github.structs.release_struct import ReleaseStruct
from gras.github.structs.repository_struct import RepositoryStruct
from gras.github.structs.stargazer_struct import StargazerStruct
from gras.github.structs.topic_struct import TopicStruct
from gras.github.structs.watcher_struct import WatcherStruct
from gras.utils import locked, timing

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
    
    @staticmethod
    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    @timing(name='process')
    def process(self):
        self.db_schema.create_tables()

        # node_ids = self._dump_anon_users()
        # self._dump_users(node_ids=node_ids, login=None)
        # self._refactor_table(id_='contributor_id', table="contributors", group_by="login, name, email")

        self._dump_repository()

        # self._dump_branches()
        # self._refactor_table(id_='id', table='branches', group_by="repo_id, name")

        # self._dump_languages()
        # self._refactor_table(id_='id', table='languages', group_by="repo_id, name")

        # self._dump_milestones()
        # self._refactor_table(id_='id', table='milestones', group_by="repo_id, number")

        # self._dump_stargazers()
        # self._refactor_table(id_='id', table='stargazers', group_by="repo_id, user_id")

        # self._dump_watchers()
        # self._refactor_table(id_='id', table='watchers', group_by="repo_id, user_id")

        self._dump_forks()
        self._refactor_table(id_='id', table='forks', group_by="repo_id, user_id")

        self._dump_topics()
        self._refactor_table(id_='id', table='topics', group_by="repo_id, url")

        self._dump_releases()
        self._refactor_table(id_='id', table='releases', group_by="repo_id, creator_id")
    
        self._dump_labels()
        self._refactor_table(id_='id', table='labels', group_by="repo_id, name")
    
        self._dump_issues()
        self._refactor_table(id_='id', table='issues', group_by="repo_id, number")
        self._refactor_table(id_='id', table='issue_assignees', group_by="repo_id, issue_id, assignee_id")
        self._refactor_table(id_='id', table='issue_labels', group_by='repo_id, issue_id, label_id')
        self._refactor_table(id_='id', table='issue_events', group_by='repo_id, issue_id, event_type, who, "when"')
        self._refactor_table(id_='id', table='issue_comments', group_by='repo_id, issue_id, commenter_id, created_at')
    
        self._dump_commits()
        self._refactor_table(id_='id', table='commits', group_by='repo_id, oid')
        self._refactor_table(id_='id', table='code_change', group_by='repo_id, oid, filename')
    
        self._dump_commit_comments()
        self._refactor_table(id_='id', table='commit_comments', group_by='repo_id, commit_id, commenter_id, created_at')
    
        self._dump_pull_requests()

    def _dump_anon_users(self, name=None, email=None):
        if name or email:
            logger.info(f"Dumping anonymous user (name: {name}, email: {email})...")
        
            obj = self.db_schema.contributors_object(
                login=None,
                name=name,
                email=email,
                created_at=None,
                updated_at=None,
                total_followers=0,
                location=None,
                is_anonymous=1
            )
        
            self._insert(self.db_schema.contributors.insert(), obj)
        else:
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
            raise GithubMinerError(msg="`_dump_users()` exception! Please consider reporting this error to the team.")
    
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
                user_id=self._get_user_id(login=node.login),
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

    def _dump_pull_request_assignees(self, node_list):
        obj_list = []

        for node in node_list:
            pr_id = node[0]
            for assignee_login in node[1]:
                obj = self.db_schema.pull_request_assignee_object(
                    repo_id=self.repo_id,
                    pr_id=pr_id,
                    assignee_id=self._get_user_id(login=assignee_login)
                )

                obj_list.append(obj)

        logger.info("Dumping Pull Request Assignees...")
        self._insert(self.db_schema.pull_request_assignees.insert(), obj_list)

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

    def _dump_pull_request_commits(self, commit_list):
        obj_list = []

        for node in commit_list:
            pr_id = node[0]
            for oid in node[1]:
                obj = self.db_schema.pull_request_commits_object(
                    repo_id=self.repo_id,
                    pr_id=pr_id,
                    commit_id=self._get_table_id('commits', 'oid', oid)
                )

                obj_list.append(obj)

        logger.info("Dumping Pull Request Commits...")
        self._insert(self.db_schema.pull_request_commits.insert(), obj_list)

    def _dump_pull_request_labels(self, label_lst):
        obj_list = []

        for node in label_lst:
            pr_id = node[0]
            for label_name in node[1]:
                obj = self.db_schema.pull_request_labels_object(
                    repo_id=self.repo_id,
                    pr_id=pr_id,
                    label_id=self._get_table_id('labels', 'name', label_name)
                )

                obj_list.append(obj)

        logger.info("Dumping Pull Request Labels...")
        self._insert(self.db_schema.pull_request_labels.insert(), obj_list)

    def _events_object_list(self, events, id_, type_):
        obj_list = []

        if type_ == "ISSUE":
            for node in events.process():
                obj = self.db_schema.issue_events_object(
                    repo_id=self.repo_id,
                    issue_id=id_,
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
        else:
            for node in events.process():
                obj = self.db_schema.pull_request_events_object(
                    repo_id=self.repo_id,
                    pr_id=id_,
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

        return obj_list

    def _dump_issue_events(self, number):
        issue_event = EventStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
            since=self.start_date,
            type_filter="issue",
            number=number
        )

        issue_id = self._get_table_id(table="issues", field="number", value=number)

        obj_list = self._events_object_list(issue_event, id_=issue_id, type_="ISSUE")

        logger.debug(f"Dumping Issue Events for Issue Number: {number}...")
        self._insert(object_=self.db_schema.issue_events.insert(), param=obj_list)

    def _dump_pull_request_events(self, number):
        pr_event = EventStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
            since=self.start_date,
            type_filter="pullRequest",
            number=number
        )

        pr_id = self._get_table_id(table="pull_requests", field="number", value=number)

        obj_list = self._events_object_list(pr_event, id_=pr_id, type_="ISSUE")

        logger.debug(f"Dumping Pull Request Events for Pull Request Number: {number}...")
        self._insert(object_=self.db_schema.pull_request_events.insert(), param=obj_list)

    def _comments_object_list(self, comments, id_, type_):
        obj_list = []

        if type_ == "ISSUE":
            for node in comments.process():
                obj = self.db_schema.issue_comments_object(
                    repo_id=self.repo_id,
                    issue_id=id_,
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
        else:
            for node in comments.process():
                obj = self.db_schema.pull_request_comments_object(
                    repo_id=self.repo_id,
                    pr_id=id_,
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

        return obj_list

    def _dump_issue_comments(self, number):
        issue_comments = CommentStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
            number=number,
            type_filter="issue"
        )

        issue_id = self._get_table_id(table="issues", field="number", value=number)

        obj_list = self._comments_object_list(issue_comments, issue_id, "ISSUE")

        logger.debug(f"Dumping Issue Comments for Issue Number: {number}...")
        self._insert(object_=self.db_schema.issue_comments.insert(), param=obj_list)

    def _dump_pull_request_comments(self, number):
        pr_comments = CommentStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
            number=number,
            type_filter="pullRequest"
        )

        pr_id = self._get_table_id(table="pull_requests", field="number", value=number)

        obj_list = self._comments_object_list(pr_comments, pr_id, "PULL_REQUEST")

        logger.debug(f"Dumping Pull Request Comments for Pull Request Number: {number}...")
        self._insert(object_=self.db_schema.pull_request_comments.insert(), param=obj_list)

    @timing(name='_dump_commits')
    def _dump_commits(self, oid=None):
        if not oid:
            commit_ids = set()
        
            for branch in self.__get_branches():
                logger.info(f"Dumping commits for branch {branch}...")
            
                commits = CommitStructV4(
                    github_token=self.token,
                    name=self.repo_name,
                    owner=self.repo_owner,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    branch=branch
                )
            
                obj_list = []
            
                for node in commits.process():
                    obj = self.db_schema.commits_object(
                        repo_id=self.repo_id,
                        oid=node.commit_id,
                        additions=node.additions,
                        deletions=node.deletions,
                        author_id=self._get_user_id(login=node.author_login, name=node.author_name,
                                                    email=node.author_email),
                        authored_date=node.authored_date,
                        committer_id=self._get_user_id(login=node.committer_login, name=node.committer_name,
                                                       email=node.committer_email),
                        committer_date=node.committed_date,
                        message=node.message,
                        num_files_changed=node.num_changed_files,
                        is_merge=node.is_merge
                    )
                
                    obj_list.append(obj)
                    commit_ids.add(node.commit_id)
            
                self._insert(object_=self.db_schema.commits.insert(), param=obj_list)
        
            commit_ids = list(commit_ids)
            logger.info(f"Total Commits: {len(commit_ids)}.")
        
            logger.info("Mining Code Change...")
            for i in range(0, len(commit_ids), mp.cpu_count()):
                # pool = mp.Pool(processes=mp.cpu_count())
                # pool.map_async(self._dump_code_change, tuple(commit_ids[i: i + mp.cpu_count()]))
                # pool.close()
                # pool.join()
            
                processes = []
                for num in commit_ids[i: i + mp.cpu_count()]:
                    p = mp.Process(target=self._dump_code_change, args=(num,))
                    p.start()
                    processes.append(p)
            
                while all([x.is_alive() for x in processes]):
                    continue
        else:
            commit = CommitStructV4(
                github_token=self.token,
                name=self.repo_name,
                owner=self.repo_owner,
                oid=oid
            ).process()
        
            obj = self.db_schema.commits_object(
                repo_id=self.repo_id,
                oid=commit.commit_id,
                additions=commit.additions,
                deletions=commit.deletions,
                author_id=self._get_user_id(login=commit.author_login, name=commit.author_name,
                                            email=commit.author_email),
                authored_date=commit.authored_date,
                committer_id=self._get_user_id(login=commit.committer_login, name=commit.committer_name,
                                               email=commit.committer_email),
                committer_date=commit.committed_date,
                message=commit.message,
                num_files_changed=commit.num_changed_files,
                is_merge=commit.is_merge
            )
        
            logger.debug(f"Dumping commit: {oid}...")
            self._insert(object_=self.db_schema.commits.insert(), param=obj)

    def _dump_code_change(self, oid):
        # TODO: Compress the patch and store (GRAS should have various compressor functions)
    
        code_change_node = CodeChangeStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
            commit_id=oid
        )
    
        obj_list = []
    
        for node in code_change_node.process():
            obj = self.db_schema.code_change_object(
                repo_id=self.repo_id,
                oid=self._get_table_id(table='commits', field='oid', value=oid),
                filename=node.filename,
                additions=node.additions,
                deletions=node.deletions,
                changes=node.changes,
                change_type=node.change_type,
                patch=node.patch
            )
        
            obj_list.append(obj)
    
        logger.info(f"Inserting code change for oid: {oid}.")
        self._insert(object_=self.db_schema.code_change.insert(), param=obj_list)

    def _dump_commit_comments(self):
        commit_comments = CommitCommentStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
        )
    
        obj_list = []
    
        for node in commit_comments.process():
            obj = self.db_schema.commit_comments_object(
                repo_id=self.repo_id,
                commenter_id=self._get_user_id(login=node.author_login),
                body=node.body,
                commit_id=self._get_table_id(table='commits', field='oid', value=node.commit_id),
                created_at=node.created_at,
                updated_at=node.updated_at,
                path=node.path,
                position=node.position,
                positive_reaction_count=node.positive_reaction_count,
                negative_reaction_count=node.negative_reaction_count,
                ambiguous_reaction_count=node.ambiguous_reaction_count
            )
        
            obj_list.append(obj)
    
        self._insert(object_=self.db_schema.commit_comments.insert(), param=obj_list)

    @timing(name='_dump_issues')
    def _dump_issues(self):
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
    
        logger.info("Dumping Issue Events...")
        for i in range(0, len(issue_list), mp.cpu_count()):
            # pool = mp.Pool(processes=mp.cpu_count())
            # pool.map_async(self._dump_issue_events, tuple(issue_list[i: i + mp.cpu_count()]))
            # pool.close()
            # pool.join()
        
            processes = []
            for num in issue_list[i: i + mp.cpu_count()]:
                p = mp.Process(target=self._dump_issue_events, args=(num,))
                p.start()
                processes.append(p)
        
            while all([x.is_alive() for x in processes]):
                continue
    
        logger.info("Dumping Issue Comments...")
        for i in range(0, len(issue_list), mp.cpu_count()):
            # pool = mp.Pool(processes=mp.cpu_count())
            # pool.map_async(self._dump_issue_comments, tuple(issue_list[i: i + mp.cpu_count()]))
            # pool.close()
            # pool.join()
        
            processes = []
            for num in issue_list[i: i + mp.cpu_count()]:
                p = mp.Process(target=self._dump_issue_comments, args=(num,))
                p.start()
                processes.append(p)
        
            while all([x.is_alive() for x in processes]):
                continue

    @timing(name='_dump_pull_requests')
    def _dump_pull_requests(self):
        logger.info("Dumping Pull Requests...")
    
        prs = PullRequestStruct(
            github_token=self.token,
            name=self.repo_name,
            owner=self.repo_owner,
            start_date=self.start_date,
            end_date=self.end_date
        )
    
        obj_list = []
        pr_assignees_lst = []
        pr_labels_lst = []
        pr_commits = []
        pr_list = []
    
        for node in prs.process():
            print("Ongoing PR:", node.number)
            obj = self.db_schema.pull_requests_object(
                repo_id=self.repo_id,
                number=node.number,
                title=node.title,
                body=node.body,
                author_id=self._get_user_id(login=node.author_login),
                num_files_changed=node.num_files_changed,
                created_at=node.created_at,
                updated_at=node.updated_at,
                additions=node.additions,
                deletions=node.deletions,
                base_ref_name=node.base_ref_name,
                base_ref_commit_id=self._get_table_id(table='commits', field='oid', value=node.base_ref_oid),
                head_ref_name=node.head_ref_name,
                head_ref_commit_id=self._get_table_id(table='commits', field='oid', value=node.head_ref_oid),
                closed=node.closed,
                closed_at=node.closed_at,
                merged=node.merged,
                merged_at=node.merged_at,
                merged_by=self._get_user_id(login=node.merged_by),
                milestone_id=self._get_table_id(table='milestones', field='number', value=node.milestone_number),
                positive_reaction_count=node.positive_reaction_count,
                negative_reaction_count=node.negative_reaction_count,
                ambiguous_reaction_count=node.ambiguous_reaction_count,
                state=node.state,
                review_decision=node.review_decision
            )

            pr_assignees_lst.append((node.number, node.assignees))
            pr_labels_lst.append((node.number, node.labels))
            pr_commits.append((node.number, node.commits))
            pr_list.append(node.number)

            obj_list.append(obj)
    
        logger.info(f"Total Pull Requests: {len(pr_list)}...")
        self._insert(self.db_schema.pull_requests.insert(), obj_list)
    
        self._dump_pull_request_assignees(pr_assignees_lst)
        self._dump_pull_request_labels(pr_labels_lst)
        self._dump_pull_request_commits(pr_commits)
    
        logger.info("Dumping Pull Request Events...")
        for i in range(0, len(pr_list), mp.cpu_count()):
            # pool = mp.Pool(processes=mp.cpu_count())
            # pool.map_async(self._dump_pull_request_events, tuple(pr_list[i: i + mp.cpu_count()]))
            # pool.close()
            # pool.join()
        
            processes = []
            for num in pr_list[i: i + mp.cpu_count()]:
                p = mp.Process(target=self._dump_pull_request_events, args=(num,))
                p.start()
                processes.append(p)
        
            while all([x.is_alive() for x in processes]):
                continue
    
        logger.info("Dumping Pull Request Comments...")
        for i in range(0, len(pr_list), mp.cpu_count()):
            # pool = mp.Pool(processes=mp.cpu_count())
            # pool.map_async(self._dump_pull_request_comments, tuple(pr_list[i: i + mp.cpu_count()]))
            # pool.close()
            # pool.join()
        
            processes = []
            for num in pr_list[i: i + mp.cpu_count()]:
                p = mp.Process(target=self._dump_pull_request_comments, args=(num,))
                p.start()
                processes.append(p)
        
            while all([x.is_alive() for x in processes]):
                continue

    def _refactor_table(self, id_, table, group_by):
        logger.info(f"Refactoring Table: {table}")
    
        deleted = self._conn.execute(
            f"""
            DELETE FROM {table}
            WHERE {id_} NOT IN
                (
                    SELECT min({id_})
                    FROM {table}
                    GROUP BY {group_by}
                );
            """
        )
    
        print("Affected:", deleted.rowcount)
    
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
        # dialect+driver://username:password@db_host:db_port/database
        
        try:
            if self.dbms == "sqlite":
                engine = create_engine(f'sqlite:///{self.db_output}', echo=self.db_log)
            elif self.dbms == 'mysql':
                engine = create_engine(f'mysql+mysqlconnector://{self.db_username}:{self.db_password}@{self.db_host}:'
                                       f'{self.db_port}', echo=self.db_log)
            elif self.dbms == 'postgres':
                engine = create_engine(f'postgresql+psycopg2://{self.db_username}:{self.db_password}@{self.db_host}:'
                                       f'{self.db_port}', echo=self.db_log)
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
    
    @locked
    def _insert(self, object_, param):
        logger.info("Inserting...")
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

    def _get_user_id(self, login, user_object=None, name=None, email=None):
        if not login and user_object:
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
                print(res[0], user_object.login)
                return res[0]
        elif login:
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
        elif name and email:
            res = self._conn.execute(
                f"""
                SELECT contributor_id
                FROM contributors
                WHERE name='{name}' AND email='{email}'
                """
            ).fetchone()
    
            if not res:
                self._dump_anon_users(name=name, email=email)
                self._get_user_id(login=None, name=name, email=email)
            else:
                return res[0]
        else:
            return None

    def _get_table_id(self, table, field, value, pk='id'):
        if value is None:
            return None
    
        res = self._conn.execute(
            f"""
            SELECT {pk}
            FROM {table}
            WHERE {field}='{value}' AND repo_id={self.repo_id}
            """
        ).fetchone()

        if not res:
            if table == "commits":
                self._dump_commits(oid=value)
                self._get_table_id(table=table, field=field, value=value)
            else:
                logger.error(f"pk not found for table: {table}, field: {field}, value: {value}.")
                # TODO: Implement create object (would have multiple if cases)
                return None
        else:
            return res[0]

    def __get_branches(self):
        res = self._conn.execute(
            f"""
            SELECT name
            FROM branches
            """
        ).fetchall()
    
        for branch in res:
            yield branch[0]

    def __del__(self):
        self._close_the_db()
