import concurrent.futures
import logging
import multiprocessing as mp

from gras.base_miner import BaseMiner
from gras.db.db_models import DBSchema
from gras.github.entity.github_models import AnonContributorModel
from gras.github.structs.branch_struct import BranchStruct
from gras.github.structs.comment_struct import CommentStruct
from gras.github.structs.commit_comment_struct import CommitCommentStruct
from gras.github.structs.commit_struct import CodeChangeStruct, CommitStructV4
from gras.github.structs.contributor_struct import (
    ContributorList, UserNodesStruct
)
from gras.github.structs.event_struct import EventDetailStruct
from gras.github.structs.fork_struct import ForkStruct
from gras.github.structs.issue_struct import IssueDetailStruct, IssueSearchStruct, IssueStruct
from gras.github.structs.label_struct import LabelStruct
from gras.github.structs.language_struct import LanguageStruct
from gras.github.structs.milestone_struct import MilestoneStruct
from gras.github.structs.pull_struct import (
    PullRequestCommitsStruct, PullRequestDetailStruct, PullRequestSearchStruct,
    PullRequestStruct
)
from gras.github.structs.release_struct import ReleaseStruct
from gras.github.structs.repository_struct import RepositoryStruct
from gras.github.structs.stargazer_struct import StargazerStruct
from gras.github.structs.topic_struct import TopicStruct
from gras.github.structs.watcher_struct import WatcherStruct
from gras.utils import timing

logger = logging.getLogger("main")
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

lock = mp.Lock()
MAX_INSERT_OBJECTS = 1000
THREADS = min(32, mp.cpu_count() + 4)


class GithubMiner(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)

        self._engine, self._conn = self._connect_to_db()
        self.db_schema = DBSchema(conn=self._conn, engine=self._engine)

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def process(self):
        self.db_schema.create_tables()
        self._dump_repository()

        if self.basic:
            self._basic_miner()

        if self.basic_extra:
            self._basic_extra_miner()

        if self.issue_tracker:
            self._issue_tracker_miner()

        if self.commit:
            self._commit_miner()

        if self.pull_tracker:
            self._pull_tracker_miner()

    @timing(name='Basic Stage', is_stage=True)
    def _basic_miner(self):
        try:
            node_ids = self._dump_anon_users()
            self._dump_users(node_ids=node_ids)
        finally:
            self._refactor_table(id_='id', table="contributors", group_by="name, email")
            self._refactor_table(id_='id', table="contributors", group_by="login, name, email")

        try:
            self._dump_branches()
        finally:
            self._refactor_table(id_='id', table='branches', group_by="repo_id, name")

        try:
            self._dump_languages()
        finally:
            self._refactor_table(id_='id', table='languages', group_by="repo_id, name")

        try:
            self._dump_milestones()
        finally:
            self._refactor_table(id_='id', table='milestones', group_by="repo_id, number")

        try:
            self._dump_topics()
        finally:
            self._refactor_table(id_='id', table='topics', group_by="repo_id, url")

        try:
            self._dump_releases()
        finally:
            self._refactor_table(id_='id', table='releases', group_by="repo_id, creator_id")

        try:
            self._dump_labels()
        finally:
            self._refactor_table(id_='id', table='labels', group_by="repo_id, name")

    @timing(name='Basic Extra Stage', is_stage=True)
    def _basic_extra_miner(self):
        self._dump_stargazers()
        self._dump_watchers()
        self._dump_forks()

    @timing(name='Issue Tracker Stage', is_stage=True)
    def _issue_tracker_miner(self):
        try:
            self._dump_issues()
        finally:
            self._refactor_table(id_='id', table='issues', group_by="repo_id, number")

        self._fetch_issue_events()
        self._fetch_issue_comments()

    @timing(name='Commit Stage', is_stage=True)
    def _commit_miner(self):
        try:
            self._dump_commits()
        finally:
            self._refactor_table(id_='id', table='commits', group_by='repo_id, oid')

        self._dump_commit_comments()
        self._fetch_code_change()

    @timing(name='Pull Tracker Stage', is_stage=True)
    def _pull_tracker_miner(self):
        try:
            self._dump_pull_requests()
        finally:
            self._refactor_table(id_='id', table='pull_requests', group_by="repo_id, number")
    
        self._fetch_pull_request_commits()
        self._fetch_pull_request_events()
        self._fetch_pull_request_comments()

    def _dump_anon_users(self):
        cont_list = ContributorList(
            name=self.repo_name,
            owner=self.repo_owner
        )
    
        node_ids = []
        obj_list = []
    
        for cont in cont_list.process():
            if isinstance(cont, AnonContributorModel):
                obj = self.db_schema.contributors_object(
                    user_type="USER",
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

    def _dump_users(self, node_ids):
        assert isinstance(node_ids, list)
    
        for i in range(0, len(node_ids), 100):
            ids_str = ",".join(node_ids[i:i + 100])
            users = UserNodesStruct(
                node_ids=ids_str
            )
        
            obj_list = []
            for node in users.process():
                obj = self.db_schema.contributors_object(
                    user_type=node.user_type,
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
    
    @timing(name='languages')
    def _dump_languages(self):
        lang = LanguageStruct(
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
    
    @timing(name='milestones')
    def _dump_milestones(self):
        milestones = MilestoneStruct(
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

    @timing(name='stargazers')
    def _dump_stargazers(self):
        logger.info("Dumping Stargazers...")

        stargazers = StargazerStruct(
            name=self.repo_name,
            owner=self.repo_owner
        )

        obj_list = []

        it = 1
        for node in stargazers.process():
            print(f"Ongoing stargazer: {it}")
            obj = self.db_schema.stargazers_object(
                repo_id=self.repo_id,
                user_id=self._get_user_id(login=None, user_object=node.user),
                starred_at=node.starred_at
            )

            obj_list.append(obj)
            it += 1

            if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                self._insert(object_=self.db_schema.stargazers.insert(), param=obj_list)
                obj_list.clear()

        self._insert(self.db_schema.stargazers.insert(), obj_list)

    @timing(name='watchers')
    def _dump_watchers(self):
        logger.info("Dumping Watchers...")

        watchers = WatcherStruct(
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

            if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                self._insert(object_=self.db_schema.watchers.insert(), param=obj_list)
                obj_list.clear()
        
        self._insert(self.db_schema.watchers.insert(), obj_list)

    @timing(name='forks')
    def _dump_forks(self):
        logger.info("Dumping Forks...")

        forks = ForkStruct(
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

            if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                self._insert(object_=self.db_schema.forks.insert(), param=obj_list)
                obj_list.clear()

        self._insert(self.db_schema.forks.insert(), obj_list)

    @timing(name='topics')
    def _dump_topics(self):
        logger.info("Dumping Topics...")

        topics = TopicStruct(
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
        
        self._insert(self.db_schema.topics.insert(), obj_list)

    @timing(name='releases')
    def _dump_releases(self):
        logger.info("Dumping Releases...")

        releases = ReleaseStruct(
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

        self._insert(self.db_schema.releases.insert(), obj_list)

    @timing(name='branches')
    def _dump_branches(self):
        logger.info("Dumping Branches...")

        branches = BranchStruct(
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

        self._insert(self.db_schema.branches.insert(), obj_list)

    @timing(name='labels')
    def _dump_labels(self):
        logger.info("Dumping Labels...")

        # TODO: Set label types as per user
        labels = LabelStruct(
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
                label_type="GENERAL"
            )

            obj_list.append(obj)

        self._insert(self.db_schema.labels.insert(), obj_list)

    @timing(name='issues')
    def _dump_issues(self, number=None):
        if number is not None:
            issue = IssueDetailStruct(
                name=self.repo_name,
                owner=self.repo_owner,
                number=number
            ).process()

            obj = self.db_schema.issues_object(
                number=issue.number,
                repo_id=self.repo_id,
                created_at=issue.created_at,
                updated_at=issue.updated_at,
                closed_at=issue.closed_at,
                title=issue.title,
                body=issue.body,
                reporter_id=self._get_user_id(login=None, user_object=issue.author),
                milestone_id=self._get_table_id(table='milestones', field='number', value=issue.milestone_number),
                positive_reaction_count=issue.positive_reaction_count,
                negative_reaction_count=issue.negative_reaction_count,
                ambiguous_reaction_count=issue.ambiguous_reaction_count,
                state=issue.state
            )

            self._insert(self.db_schema.issues.insert(), obj)
        else:
            if self.full:
                logger.info("Dumping Issues...")
                issues = IssueStruct(
                    name=self.repo_name,
                    owner=self.repo_owner
                )
            else:
                logger.info("Dumping Issues using Search API...")
                issues = IssueSearchStruct(
                    name=self.repo_name,
                    owner=self.repo_owner,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    chunk_size=self.chunk_size
                )

            obj_list = []
            issue_assignees_lst = []
            issue_labels_lst = []
            issue_list = []

            it = 0
            for node in issues.process():
                print(f"Ongoing {it} --> {node.number}")
                it += 1
                obj = self.db_schema.issues_object(
                    number=node.number,
                    repo_id=self.repo_id,
                    created_at=node.created_at,
                    updated_at=node.updated_at,
                    closed_at=node.closed_at,
                    title=node.title,
                    body=node.body,
                    reporter_id=self._get_user_id(login=None, user_object=node.author),
                    milestone_id=self._get_table_id(table='milestones', field='number', value=node.milestone_number),
                    positive_reaction_count=node.positive_reaction_count,
                    negative_reaction_count=node.negative_reaction_count,
                    ambiguous_reaction_count=node.ambiguous_reaction_count,
                    state=node.state
                )

                issue_assignees_lst.append((node.number, node.assignees))
                issue_labels_lst.append((node.number, node.labels))

                if node.number not in issue_list:
                    issue_list.append(node.number)
                    obj_list.append(obj)

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    logger.debug(f"Inserting {MAX_INSERT_OBJECTS} issues...")
                    self._insert(object_=self.db_schema.issues.insert(), param=obj_list)
                    obj_list.clear()
                    logger.debug("Success!")

            logger.info(f"Total Issues: {len(issue_list)}...")
            self._insert(self.db_schema.issues.insert(), obj_list)

            self._dump_issue_assignees(issue_assignees_lst)
            self._dump_issue_labels(issue_labels_lst)

    @timing(name='issue_assignees')
    def _dump_issue_assignees(self, node_list):
        logger.info("Dumping Issue Assignees...")

        obj_list = []

        for node in node_list:
            number = node[0]
            for assignee_login in node[1]:
                obj = self.db_schema.issue_assignees_object(
                    repo_id=self.repo_id,
                    issue_id=self._get_table_id(table="issues", field="number", value=number),
                    assignee_id=self._get_user_id(login=assignee_login)
                )
                
                obj_list.append(obj)

        self._insert(self.db_schema.issue_assignees.insert(), obj_list)

    @timing(name='issue_labels')
    def _dump_issue_labels(self, label_list):
        logger.info("Dumping Issue Labels...")

        obj_list = []

        for node in label_list:
            number = node[0]
            for label_name in node[1]:
                obj = self.db_schema.issue_labels_object(
                    repo_id=self.repo_id,
                    issue_id=self._get_table_id(table="issues", field="number", value=number),
                    label_id=self._get_table_id('labels', 'name', label_name)
                )
                
                obj_list.append(obj)

        self._insert(self.db_schema.issue_labels.insert(), obj_list)
    
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

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.issue_events.insert(), param=obj_list)
                    obj_list.clear()
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

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.pull_request_events.insert(), param=obj_list)
                    obj_list.clear()

        return obj_list
    
    def _dump_issue_events(self, number):
        issue_event = EventDetailStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            since=self.start_date if not self.full else None,
            type_filter="issue",
            number=number
        )

        issue_id = self._get_table_id(table="issues", field="number", value=number)

        obj_list = self._events_object_list(issue_event, id_=issue_id, type_="ISSUE")

        logger.debug(f"Dumping Issue Events for Issue Number: {number}...")
        self._insert(object_=self.db_schema.issue_events.insert(), param=obj_list)

    @timing(name='issue_events')
    def _fetch_issue_events(self):
        logger.info("Dumping Issue Events...")

        for issues in self.__get_issues('issue_events'):
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_issue_events, iss): iss for iss in issues}
                for future in concurrent.futures.as_completed(process):
                    number = process[future]
                    logger.debug(f"Inserted events for issue number: {number}")

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

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.issue_comments.insert(), param=obj_list)
                    obj_list.clear()
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

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.pull_request_comments.insert(), param=obj_list)
                    obj_list.clear()

        return obj_list

    def _dump_issue_comments(self, number):
        logger.debug(f"Dumping Issue Comments for Issue Number: {number}...")

        issue_comments = CommentStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            number=number,
            type_filter="issue"
        )

        issue_id = self._get_table_id(table="issues", field="number", value=number)

        obj_list = self._comments_object_list(issue_comments, issue_id, "ISSUE")

        self._insert(object_=self.db_schema.issue_comments.insert(), param=obj_list)

    @timing(name='issue_comments')
    def _fetch_issue_comments(self):
        logger.info("Dumping Issue Comments...")

        for issues in self.__get_issues('issue_comments'):
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_issue_comments, iss): iss for iss in issues}
                for future in concurrent.futures.as_completed(process):
                    number = process[future]
                    future.result()
                    logger.debug(f"Inserted comments for Issue number: {number}")

    def _fetch_code_change(self):
        logger.info("Mining Code Change...")

        for commits in self.__get_commit_oids():
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_code_change, oid): oid for oid in commits}
                for future in concurrent.futures.as_completed(process):
                    oid = process[future]
                    future.result()
                    logger.debug(f"Inserted code change for oid: {oid}")

    def _dump_commits(self, oid=None):
        if not oid:
            commit_ids = []

            for branch in self.__get_branches():
                logger.info(f"Dumping commits for branch {branch}...")

                if self.full:
                    commits = CommitStructV4(
                        name=self.repo_name,
                        owner=self.repo_owner,
                        branch=branch
                    )
                else:
                    commits = CommitStructV4(
                        name=self.repo_name,
                        owner=self.repo_owner,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        branch=branch
                    )

                obj_list = []

                it = 0
                for node in commits.process():
                    print(f"Ongoing {it} --> {node.commit_id}")
                    it += 1
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

                    if node.commit_id in commit_ids:
                        logger.debug("Tree search complete! Changing branch...")
                        break

                    if node.commit_id not in commit_ids:
                        commit_ids.append(node.commit_id)
                        obj_list.append(obj)

                    if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                        logger.debug(f"Inserting {MAX_INSERT_OBJECTS} commits...")
                        self._insert(object_=self.db_schema.commits.insert(), param=obj_list)
                        obj_list.clear()
                        logger.debug("Success!")

                self._insert(object_=self.db_schema.commits.insert(), param=obj_list)
        else:
            logger.debug(f"Dumping commit: {oid}...")

            com = CommitStructV4(
                name=self.repo_name,
                owner=self.repo_owner,
                oid=oid
            )

            obj_list = []

            for commit in com.process():
                obj = self.db_schema.commits_object(
                    repo_id=self.repo_id,
                    oid=oid,
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

                obj_list.append(obj)

            self._insert(object_=self.db_schema.commits.insert(), param=obj_list)

    def _dump_code_change(self, oid):
        logger.info(f"Inserting code change for oid: {oid}.")

        # TODO: Compress the patch and store (GRAS should have various compressor functions)
        code_change_node = CodeChangeStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            commit_id=oid
        )

        obj_list = []

        for node in code_change_node.process():
            commit_id = self._get_table_id(table='commits', field='oid', value=oid)
            logger.debug(f"Dumping for sha: {oid}, commit-id: {commit_id}, filename: {node.filename}")
            obj = self.db_schema.code_change_object(
                repo_id=self.repo_id,
                commit_id=commit_id,
                filename=node.filename,
                additions=node.additions,
                deletions=node.deletions,
                changes=node.changes,
                change_type=node.change_type,
                patch=node.patch
            )

            obj_list.append(obj)

        self._insert(object_=self.db_schema.code_change.insert(), param=obj_list)
    
    @timing(name='commit_comments')
    def _dump_commit_comments(self):
        logger.info("Dumping Commit Comments...")
        
        commit_comments = CommitCommentStruct(
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

            if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                self._insert(object_=self.db_schema.commit_comments.insert(), param=obj_list)
                obj_list.clear()
        
        self._insert(object_=self.db_schema.commit_comments.insert(), param=obj_list)

    @timing(name='pull_requests')
    def _dump_pull_requests(self, number=None):
        if number is not None:
            pr = PullRequestDetailStruct(
                name=self.repo_name,
                owner=self.repo_owner,
                number=number
            ).process()

            obj = self.db_schema.pull_requests_object(
                repo_id=self.repo_id,
                number=pr.number,
                title=pr.title,
                body=pr.body,
                author_id=self._get_user_id(login=None, user_object=pr.author),
                num_files_changed=pr.num_files_changed,
                created_at=pr.created_at,
                updated_at=pr.updated_at,
                additions=pr.additions,
                deletions=pr.deletions,
                base_ref_name=pr.base_ref_name,
                base_ref_commit_id=self._get_table_id(table='commits', field='oid', value=pr.base_ref_oid),
                head_ref_name=pr.head_ref_name,
                head_ref_commit_id=self._get_table_id(table='commits', field='oid', value=pr.head_ref_oid),
                closed=pr.closed,
                closed_at=pr.closed_at,
                merged=pr.merged,
                merged_at=pr.merged_at,
                merged_by=self._get_user_id(login=None, user_object=pr.merged_by),
                milestone_id=self._get_table_id(table='milestones', field='number', value=pr.milestone_number),
                positive_reaction_count=pr.positive_reaction_count,
                negative_reaction_count=pr.negative_reaction_count,
                ambiguous_reaction_count=pr.ambiguous_reaction_count,
                state=pr.state,
                review_decision=pr.review_decision
            )

            self._insert(self.db_schema.pull_requests.insert(), obj)
        else:
            if self.full:
                logger.info("Dumping Pull Requests...")
                prs = PullRequestStruct(
                    name=self.repo_name,
                    owner=self.repo_owner,
                    limit=50
                )
            else:
                logger.info("Dumping Pull Requests using Search API...")
                prs = PullRequestSearchStruct(
                    name=self.repo_name,
                    owner=self.repo_owner,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    chunk_size=self.chunk_size,
                    limit=50
                )

            obj_list = []
            pr_assignees_lst = []
            pr_labels_lst = []
            pr_list = []

            for node in prs.process():
                logger.debug(f"Ongoing PR: {node.number}")
                obj = self.db_schema.pull_requests_object(
                    repo_id=self.repo_id,
                    number=node.number,
                    title=node.title,
                    body=node.body,
                    author_id=self._get_user_id(login=None, user_object=node.author),
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
                    merged_by=self._get_user_id(login=None, user_object=node.merged_by),
                    milestone_id=self._get_table_id(table='milestones', field='number', value=node.milestone_number),
                    positive_reaction_count=node.positive_reaction_count,
                    negative_reaction_count=node.negative_reaction_count,
                    ambiguous_reaction_count=node.ambiguous_reaction_count,
                    state=node.state,
                    review_decision=node.review_decision
                )

                pr_assignees_lst.append((node.number, node.assignees))
                pr_labels_lst.append((node.number, node.labels))
                pr_list.append(node.number)

                obj_list.append(obj)

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    logger.debug(f"Inserting {MAX_INSERT_OBJECTS} pull requests...")
                    self._insert(object_=self.db_schema.pull_requests.insert(), param=obj_list)
                    obj_list.clear()
                    logger.debug("Success!")

            logger.info(f"Total Pull Requests: {len(pr_list)}...")
            self._insert(self.db_schema.pull_requests.insert(), obj_list)

            self._dump_pull_request_assignees(pr_assignees_lst)
            self._dump_pull_request_labels(pr_labels_lst)

    @timing(name='pull_request_assignees')
    def _dump_pull_request_assignees(self, node_list):
        logger.info("Dumping Pull Request Assignees...")

        obj_list = []

        for node in node_list:
            number = node[0]
            for assignee_login in node[1]:
                obj = self.db_schema.pull_request_assignee_object(
                    repo_id=self.repo_id,
                    pr_id=self._get_table_id(table="pull_requests", field="number", value=number),
                    assignee_id=self._get_user_id(login=assignee_login)
                )
                
                obj_list.append(obj)
                
                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.pull_request_assignees.insert(), param=obj_list)
                    obj_list.clear()

        self._insert(self.db_schema.pull_request_assignees.insert(), obj_list)

    @timing(name='pull_request_labels')
    def _dump_pull_request_labels(self, label_lst):
        logger.info("Dumping Pull Request Labels...")

        obj_list = []

        for node in label_lst:
            number = node[0]
            for label_name in node[1]:
                obj = self.db_schema.pull_request_labels_object(
                    repo_id=self.repo_id,
                    pr_id=self._get_table_id(table="pull_requests", field="number", value=number),
                    label_id=self._get_table_id('labels', 'name', label_name)
                )

                obj_list.append(obj)

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.pull_request_labels.insert(), param=obj_list)
                    obj_list.clear()

        self._insert(self.db_schema.pull_request_labels.insert(), obj_list)

    def _dump_pull_request_commits(self, number):
        logger.debug(f"Dumping Pull Request Commits for Pull Request Number: {number}...")

        pr_commit = PullRequestCommitsStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            number=number
        )

        obj_list = []
        for node in pr_commit.process():
            obj = self.db_schema.pull_request_commits_object(
                repo_id=self.repo_id,
                pr_id=self._get_table_id(table="pull_requests", field="number", value=number),
                commit_id=self._get_table_id('commits', 'oid', node.oid)
            )

            obj_list.append(obj)

        self._insert(self.db_schema.pull_request_commits.insert(), obj_list)

    @timing(name="pull_request_commits")
    def _fetch_pull_request_commits(self):
        logger.info("Dumping Pull Request Commits...")

        for pr_commits in self.__get_pull_requests(table="pull_request_commits"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_pull_request_commits, pr): pr for pr in pr_commits}
                for future in concurrent.futures.as_completed(process):
                    number = process[future]
                    future.result()
                    logger.debug(f"Inserted Commits for PR Number: {number}")

    def _dump_pull_request_events(self, number):
        logger.debug(f"Dumping Pull Request Events for Pull Request Number: {number}...")

        pr_event = EventDetailStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            since=self.start_date if not self.full else None,
            type_filter="pullRequest",
            number=number
        )

        pr_id = self._get_table_id(table="pull_requests", field="number", value=number)

        obj_list = self._events_object_list(pr_event, id_=pr_id, type_="PULL_REQUEST")

        self._insert(object_=self.db_schema.pull_request_events.insert(), param=obj_list)

    @timing(name="pull_request_events")
    def _fetch_pull_request_events(self):
        logger.info("Dumping Pull Request Events...")

        for prs in self.__get_pull_requests('pull_request_events'):
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_issue_events, pr): pr for pr in prs}
                for future in concurrent.futures.as_completed(process):
                    number = process[future]
                    future.result()
                    logger.debug(f"Inserted Events for PR Number: {number}")

    def _dump_pull_request_comments(self, number):
        logger.debug(f"Dumping Pull Request Comments for Pull Request Number: {number}...")

        pr_comments = CommentStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            number=number,
            type_filter="pullRequest"
        )

        pr_id = self._get_table_id(table="pull_requests", field="number", value=number)

        obj_list = self._comments_object_list(pr_comments, pr_id, "PULL_REQUEST")

        self._insert(object_=self.db_schema.pull_request_comments.insert(), param=obj_list)

    @timing(name='pull_request_comments')
    def _fetch_pull_request_comments(self):
        logger.info("Dumping Pull Request Comments...")

        for prs in self.__get_pull_requests('pull_request_comments'):
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_pull_request_comments, pr): pr for pr in prs}
                for future in concurrent.futures.as_completed(process):
                    number = process[future]
                    future.result()
                    logger.debug(f"Inserted Comments for PR number: {number}")
    
    def _get_user_id(self, login, user_object=None, name=None, email=None):
        if not login and user_object:
            res = self._conn.execute(
                f"""
                SELECT id
                FROM contributors
                WHERE login="{user_object.login}"
                """
            ).fetchone()

            if not res:
                has_dumped = self._dump_user_object(login=None, user_object=user_object,
                                                    object_=self.db_schema.contributors.insert())
                if has_dumped:
                    return self._get_user_id(user_object.login)
                else:
                    return None
            else:
                return res[0]
        elif login:
            res = self._conn.execute(
                f"""
                SELECT id
                FROM contributors
                WHERE login="{login}"
                """
            ).fetchone()

            if not res:
                has_dumped = self._dump_user_object(login=login, object_=self.db_schema.contributors.insert())
                if has_dumped:
                    return self._get_user_id(login)
                else:
                    return None
            else:
                return res[0]
        elif name and email:
            res = self._conn.execute(
                f"""
                SELECT id
                FROM contributors
                WHERE name="{name}" AND email="{email}"
                """
            ).fetchone()

            if not res:
                has_dumped = self._dump_anon_user_object(name=name, email=email,
                                                         object_=self.db_schema.contributors.insert())
                if has_dumped:
                    return self._get_user_id(login=None, name=name, email=email)
                else:
                    return None
            else:
                return res[0]
        else:
            return None
    
    def _get_table_id(self, table, field, value, pk='id', toggle=False):
        if value is None:
            return None

        res = self._conn.execute(
            f"""
            SELECT {pk}
            FROM {table}
            WHERE {field}="{value}" AND repo_id={self.repo_id}
            """
        ).fetchone()

        if not res:
            if table == "commits":
                if not toggle:
                    self._dump_commits(oid=value)
                    return self._get_table_id(table=table, field=field, value=value, toggle=True)
                else:
                    logger.debug(f"Commit oid: {value} has been deleted! Returning `None`.")
                    return None
            elif table == "issues":
                if not toggle:
                    self._dump_issues(number=value)
                    return self._get_table_id(table=table, field=field, value=value, toggle=True)
                else:
                    logger.debug(f"Issue number: {value} has been deleted! Returning `None`.")
                    return None
            elif table == "pull_requests":
                if not toggle:
                    self._dump_pull_requests(number=value)
            else:
                logger.error(f"pk not found for table: {table}, field: {field}, value: {value}.")
                # TODO: Implement remaining create objects (would have multiple if cases)
                return None
        else:
            return res[0]

    def __get_issues(self, table):
        res = self._conn.execute(
            f"""
            SELECT DISTINCT number
            FROM issues
            WHERE id NOT IN (
                SELECT DISTINCT issue_id
                FROM {table}
            )
            """
        ).fetchall()

        for r in range(0, len(res), THREADS):
            yield [x[0] for x in res[r:r + THREADS]]

    def __get_pull_requests(self, table):
        res = self._conn.execute(
            f"""
            SELECT DISTINCT number
            FROM pull_requests
            WHERE id NOT IN (
                SELECT DISTINCT pr_id
                FROM {table}
            )
            """
        ).fetchall()

        for r in range(0, len(res), THREADS):
            yield [x[0] for x in res[r:r + THREADS]]

    def __get_commit_oids(self):
        res = self._conn.execute(
            f"""
            SELECT DISTINCT oid
            FROM commits
            """
        ).fetchall()

        for r in range(0, len(res), THREADS):
            yield [x[0] for x in res[r:r + THREADS]]

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
