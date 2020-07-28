import concurrent.futures
import logging
import multiprocessing as mp
import os

from gras.base_miner import BaseMiner
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
from gras.utils import locked, timing

logger = logging.getLogger("main")
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

lock = mp.Lock()
MAX_INSERT_OBJECTS = 500
THREADS = min(32, mp.cpu_count() + 4)


class GithubMiner(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)

        self._initialise_db()

        if args.dbms == "sqlite":
            self._conn.execute("PRAGMA foreign_keys=ON")

        self.issues = {}
        self.pull_requests = {}
        self.commits = {}
        self.labels = {}
        self.milestones = {}

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def process(self):
        self.__init_users()
        self.__init_basic()

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

    def __init_users(self):
        res = self._conn.execute(
            """
            SELECT login, name, email, id
            FROM contributors
            """
        ).fetchall()

        for row in res:
            self.login_id[row[0]] = row[3]
            if row[1] or row[2]:
                self.name_email_id[self.Name_Email(name=row[1], email=row[2])] = row[3]

    def __init_basic(self):
        res = self._conn.execute(
            """
            SELECT name, id
            FROM labels
            """
        ).fetchall()

        for row in res:
            self.labels[row[0]] = row[1]

        res = self._conn.execute(
            """
            SELECT number, id
            FROM milestones
            """
        ).fetchall()

        for row in res:
            self.milestones[row[0]] = row[1]

    def __init_issues(self):
        res = self._conn.execute(
            f"""
            SELECT number, id
            FROM issues
            """
        ).fetchall()

        for row in res:
            self.issues[row[0]] = row[1]

    def __init_pull_requests(self):
        res = self._conn.execute(
            f"""
            SELECT number, id
            FROM pull_requests
            """
        ).fetchall()

        for row in res:
            self.pull_requests[row[0]] = row[1]

    def __init_commits(self):
        res = self._conn.execute(
            f"""
            SELECT oid, id
            FROM commits
            """
        ).fetchall()

        for row in res:
            self.commits[row[0]] = row[1]

    def __add_object_to_cache(self, table, where, key):
        res = self._conn.execute(
            f"""
            SELECT id 
            FROM {table}
            WHERE {where}
            """
        ).fetchone()

        if table == "issues":
            self.issues[key] = res[0]
        elif table == "pull_requests":
            self.pull_requests[key] = res[0]
        else:
            raise NotImplementedError

    @timing(name='Basic Stage', is_stage=True)
    def _basic_miner(self):
        node_ids = self._dump_anon_users()
        self._dump_users(node_ids=node_ids)

        inserted = self._dump_branches()
        if inserted:
            self._refactor_table(id_='id', table='branches', group_by="repo_id, name")

        inserted = self._dump_languages()
        if inserted:
            self._refactor_table(id_='id', table='languages', group_by="repo_id, name")

        inserted = self._dump_milestones()
        if inserted:
            self._refactor_table(id_='id', table='milestones', group_by="repo_id, number")

        inserted = self._dump_topics()
        if inserted:
            self._refactor_table(id_='id', table='topics', group_by="repo_id, url")

        inserted = self._dump_releases()
        if inserted:
            self._refactor_table(id_='id', table='releases', group_by="repo_id, name")

        inserted = self._dump_labels()
        if inserted:
            self._refactor_table(id_='id', table='labels', group_by="repo_id, name")

        self.__init_basic()

    @timing(name='Basic Extra Stage', is_stage=True)
    def _basic_extra_miner(self):
        self._dump_stargazers()
        self._dump_watchers()
        self._dump_forks()

    @timing(name='Issue Tracker Stage', is_stage=True)
    def _issue_tracker_miner(self):
        self.__init_issues()

        try:
            self._dump_issues()
        finally:
            self._refactor_table(id_='id', table='issues', group_by="repo_id, number")

        self._fetch_issue_events()
        self._fetch_issue_comments()

    @timing(name='Commit Stage', is_stage=True)
    def _commit_miner(self):
        self.__init_commits()

        try:
            self._dump_commits()
        finally:
            self._refactor_table(id_='id', table='commits', group_by='repo_id, oid')

        self._dump_commit_comments()
        self._refactor_table(id_='id', table='commit_comments', group_by='repo_id, commenter_id, commit_id, created_at')

        self._fetch_code_change()

    @timing(name='Pull Tracker Stage', is_stage=True)
    def _pull_tracker_miner(self):
        self.__init_pull_requests()
        self.__init_commits()

        # try:
        #     self._dump_pull_requests()
        # finally:
        #     self._refactor_table(id_='id', table='pull_requests', group_by="repo_id, number")

        # self.__init_pull_requests()

        self._fetch_pull_request_commits()
        self._fetch_pull_request_events()
        self._fetch_pull_request_comments()

    def _dump_anon_users(self):
        cont_list = ContributorList(
            name=self.repo_name,
            owner=self.repo_owner
        )

        res = self._conn.execute(
            f"""
            SELECT DISTINCT email
            FROM contributors
            """
        ).fetchall()

        dumped_emails = [x[0] for x in res]

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

                if cont.email not in dumped_emails:
                    obj_list.append(obj)
            else:
                node_ids.append("\"" + cont + "\"")

        logger.info("Dumping Anonymous Contributors...")
        self._insert(self.db_schema.contributors.insert(), obj_list)

        return node_ids

    def _dump_users(self, node_ids):
        assert isinstance(node_ids, list)

        res = self._conn.execute(
            f"""
            SELECT DISTINCT login
            FROM contributors
            """
        ).fetchall()

        dumped_login = [x[0] for x in res]

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

                if node.login not in dumped_login:
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
        return self._insert(self.db_schema.languages.insert(), obj_list)

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
        return self._insert(self.db_schema.milestones.insert(), obj_list)

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

        return self._insert(self.db_schema.topics.insert(), obj_list)

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

        return self._insert(self.db_schema.releases.insert(), obj_list)

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

        return self._insert(self.db_schema.branches.insert(), obj_list)

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

        return self._insert(self.db_schema.labels.insert(), obj_list)

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
            self.__add_object_to_cache(table="issues", where=f"number={number}", key=number)
        else:
            res = self._conn.execute(
                f"""
                SELECT DISTINCT number
                FROM issues
                """
            ).fetchall()

            dumped_issues = [x[0] for x in res]

            if self.full:
                logger.info("Dumping Issues...")

                res = self._conn.execute(
                    f"""
                    SELECT max(created_at)
                    FROM issues
                    """
                ).fetchone()

                if res[0]:
                    try:
                        since = "T".join(res[0].split())
                    except Exception:
                        since = res[0].isoformat()
                else:
                    since = None

                issues = IssueStruct(
                    name=self.repo_name,
                    owner=self.repo_owner,
                    since=since
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
            issue_list = []
            assignee_list = []
            label_list = []

            it = len(dumped_issues) + 1
            for node in issues.process():
                if node.number not in dumped_issues:
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
                        reporter_id=self._get_user_id(login=None, user_object=node.author) if node.author else None,
                        milestone_id=self._get_table_id(table='milestones', field='number',
                                                        value=node.milestone_number),
                        positive_reaction_count=node.positive_reaction_count,
                        negative_reaction_count=node.negative_reaction_count,
                        ambiguous_reaction_count=node.ambiguous_reaction_count,
                        state=node.state
                    )

                    if node.number not in issue_list:
                        issue_list.append(node.number)
                        obj_list.append(obj)

                        if node.assignees:
                            assignee_list.append((node.number, node.assignees))

                        if node.labels:
                            label_list.append((node.number, node.labels))

                    if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                        logger.debug(f"Inserting {MAX_INSERT_OBJECTS} issues...")
                        self._insert(object_=self.db_schema.issues.insert(), param=obj_list)
                        obj_list.clear()
                        logger.debug("Success!")

                        objects = []

                        for number, assignees in assignee_list:
                            objects.extend(self._dump_issue_assignees(number, assignees))

                        self._insert(self.db_schema.issue_assignees.insert(), objects)
                        objects.clear()

                        for number, labels in label_list:
                            objects.extend(self._dump_issue_labels(number, labels))

                        self._insert(self.db_schema.issue_labels.insert(), objects)
                        del objects

                        assignee_list.clear()
                        label_list.clear()
                else:
                    print("Skipped:", node.number)

            logger.info(f"Total Issues: {len(issue_list)}...")
            self._insert(self.db_schema.issues.insert(), obj_list)

    @timing(name='issue_assignees')
    def _dump_issue_assignees(self, number, assignees):
        logger.info("Dumping Issue Assignees...")

        obj_list = []

        for assignee_login in assignees:
            try:
                issue_id = self.issues[number]
            except KeyError:
                issue_id = self._get_table_id(table="issues", field="number", value=number)
                self.issues[number] = issue_id

            obj = self.db_schema.issue_assignees_object(
                repo_id=self.repo_id,
                issue_id=issue_id,
                assignee_id=self._get_user_id(login=assignee_login)
            )

            obj_list.append(obj)

        return obj_list

    @timing(name='issue_labels')
    def _dump_issue_labels(self, number, labels):
        logger.info("Dumping Issue Labels...")

        obj_list = []

        for label_name in labels:
            try:
                issue_id = self.issues[number]
            except KeyError:
                issue_id = self._get_table_id(table="issues", field="number", value=number)
                self.issues[number] = issue_id

            try:
                label_id = self.labels[label_name]
            except KeyError:
                raise Exception("_dump_issue_labels: No label present!")

            obj = self.db_schema.issue_labels_object(
                repo_id=self.repo_id,
                issue_id=issue_id,
                label_id=label_id
            )

            obj_list.append(obj)

        return obj_list

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

        try:
            issue_id = self.issues[number]
        except KeyError:
            issue_id = self._get_table_id(table="issues", field="number", value=number)
            self.issues[issue_id] = number

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

                    if future.exception():
                        exception = future.exception()
                        logger.error(f"_fetch_issue_events: {exception}")
                        os._exit(1)

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

        try:
            issue_id = self.issues[number]
        except KeyError:
            issue_id = self._get_table_id(table="issues", field="number", value=number)
            self.issues[number] = issue_id

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

                    if future.exception():
                        exception = future.exception()
                        logger.error(f"_fetch_issue_comments: {exception}")
                        os._exit(1)

    def _fetch_code_change(self):
        logger.info("Mining Code Change...")

        for commits in self.__get_commit_oids():
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_code_change, oid): oid for oid in commits}
                for future in concurrent.futures.as_completed(process):
                    oid = process[future]
                    future.result()
                    logger.debug(f"Inserted code change for oid: {oid}")

                    if future.exception():
                        exception = future.exception()
                        logger.error(f"_fetch_code_change: {exception}")
                        os._exit(1)

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

            for p in com.process():
                commit = p

                if commit is None:
                    return None

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

                self._insert(object_=self.db_schema.commits.insert(), param=obj)

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
            try:
                commit_id = self.commits[node.commit_id]
            except KeyError:
                commit_id = self._get_table_id(table='commits', field='oid', value=node.commit_id)
                self.commits[node.commit_id] = commit_id

            obj = self.db_schema.commit_comments_object(
                repo_id=self.repo_id,
                commenter_id=self._get_user_id(login=node.author_login),
                body=node.body,
                commit_id=commit_id,
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
            res = self._conn.execute(
                f"""
                SELECT DISTINCT number
                FROM pull_requests
                """
            ).fetchall()

            dumped_prs = [x[0] for x in res]

            if self.full:
                logger.info("Dumping Pull Requests...")

                res = self._conn.execute(
                    f"""
                    SELECT MAX(number) 
                    FROM pull_requests
                    """
                ).fetchone()

                prs = PullRequestStruct(
                    name=self.repo_name,
                    owner=self.repo_owner,
                    limit=50
                )

                if res[0]:
                    after = prs.skip_iterator(res[0])
                    print(after)
                    if after is None:
                        after = "null"
                else:
                    after = None

                print("AFTER:", after)
                prs = PullRequestStruct(
                    name=self.repo_name,
                    owner=self.repo_owner,
                    limit=50,
                    after=after
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
            assignee_list = []
            label_list = []
            total_prs = 0

            it = len(dumped_prs) + 1
            for node in prs.process():
                if node.number not in dumped_prs:
                    print(f"Ongoing {it} --> {node.number}")
                    it += 1

                    try:
                        base_ref_commit_id = self.commits[node.base_ref_oid]
                    except KeyError:
                        base_ref_commit_id = self._get_table_id(table='commits', field='oid', value=node.base_ref_oid)
                        self.commits[node.base_ref_oid] = base_ref_commit_id

                    try:
                        head_red_commit_id = self.commits[node.head_ref_oid]
                    except KeyError:
                        head_red_commit_id = self._get_table_id(table='commits', field='oid', value=node.head_ref_oid)
                        self.commits[node.head_ref_oid] = head_red_commit_id

                    try:
                        milestone_id = self.milestones[node.milestone_number]
                    except KeyError:
                        milestone_id = self._get_table_id(table='milestones', field='number',
                                                          value=node.milestone_number)
                        self.milestones[node.milestone_number] = milestone_id

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
                        base_ref_commit_id=base_ref_commit_id,
                        head_ref_name=node.head_ref_name,
                        head_ref_commit_id=head_red_commit_id,
                        closed=node.closed,
                        closed_at=node.closed_at,
                        merged=node.merged,
                        merged_at=node.merged_at,
                        merged_by=self._get_user_id(login=None, user_object=node.merged_by),
                        milestone_id=milestone_id,
                        positive_reaction_count=node.positive_reaction_count,
                        negative_reaction_count=node.negative_reaction_count,
                        ambiguous_reaction_count=node.ambiguous_reaction_count,
                        state=node.state,
                        review_decision=node.review_decision
                    )

                    if node.assignees:
                        assignee_list.append((node.number, node.assignees))

                    if node.labels:
                        label_list.append((node.number, node.labels))

                    total_prs += 1

                    obj_list.append(obj)

                    if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                        logger.debug(f"Inserting {MAX_INSERT_OBJECTS} pull requests...")
                        self._insert(object_=self.db_schema.pull_requests.insert(), param=obj_list)
                        obj_list.clear()
                        logger.debug("Success!")

                        objects = []

                        for number, assignees in assignee_list:
                            temp = self._dump_pull_request_assignees(number, assignees)
                            if temp:
                                objects.extend(temp)

                        self._insert(self.db_schema.pull_request_assignees.insert(), objects)
                        objects.clear()

                        for number, labels in label_list:
                            temp = self._dump_pull_request_labels(number, labels)
                            if temp:
                                objects.extend(temp)

                        self._insert(self.db_schema.pull_request_labels.insert(), objects)
                        del objects

                        assignee_list.clear()
                        label_list.clear()
                else:
                    logger.debug(f"Skipped: {node.number}")

            logger.info(f"Total Pull Requests: {total_prs}...")
            self._insert(self.db_schema.pull_requests.insert(), obj_list)

    @timing(name='pull_request_assignees')
    def _dump_pull_request_assignees(self, number, assignees):
        res = self._conn.execute(
            f"""
            SELECT id
            FROM pull_request_assignees
            WHERE pr_id = {number}
            LIMIT 1
            """
        ).fetchone()

        if not res:
            logger.info(f"Dumping Assignees for Pull Request: {number}...")

            obj_list = []

            for assignee_login in assignees:
                try:
                    pr_id = self.pull_requests[number]
                except KeyError:
                    pr_id = self._get_table_id(table="pull_requests", field="number", value=number)
                    self.pull_requests[number] = pr_id

                obj = self.db_schema.pull_request_assignee_object(
                    repo_id=self.repo_id,
                    pr_id=pr_id,
                    assignee_id=self._get_user_id(login=assignee_login)
                )

                obj_list.append(obj)

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.pull_request_assignees.insert(), param=obj_list)
                    obj_list.clear()

            return obj_list

    @timing(name='pull_request_labels')
    def _dump_pull_request_labels(self, number, labels):
        res = self._conn.execute(
            f"""
            SELECT id
            FROM pull_request_labels
            WHERE pr_id = {number}
            LIMIT 1
            """
        ).fetchone()

        if not res:
            logger.info(f"Dumping Labels for Pull Request: {number}...")

            obj_list = []

            for label_name in labels:
                try:
                    pr_id = self.pull_requests[number]
                except KeyError:
                    pr_id = self._get_table_id(table="pull_requests", field="number", value=number)
                    self.pull_requests[number] = pr_id

                obj = self.db_schema.pull_request_labels_object(
                    repo_id=self.repo_id,
                    pr_id=pr_id,
                    label_id=self._get_table_id('labels', 'name', label_name)
                )

                obj_list.append(obj)

                if len(obj_list) % MAX_INSERT_OBJECTS == 0:
                    self._insert(object_=self.db_schema.pull_request_labels.insert(), param=obj_list)
                    obj_list.clear()

            return obj_list

    def _dump_pull_request_commits(self, number):
        logger.debug(f"Dumping Pull Request Commits for Pull Request Number: {number}...")

        pr_commit = PullRequestCommitsStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            number=number
        )

        obj_list = []
        for node in pr_commit.process():
            try:
                pr_id = self.pull_requests[number]
            except KeyError:
                pr_id = self._get_table_id(table="pull_requests", field="number", value=number)
                self.pull_requests[number] = pr_id

            try:
                commit_id = self.commits[node.oid]
            except KeyError:
                commit_id = self._get_table_id('commits', 'oid', node.oid)
                self.commits[node.oid] = commit_id

            obj = self.db_schema.pull_request_commits_object(
                repo_id=self.repo_id,
                pr_id=pr_id,
                commit_id=commit_id
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

                    if future.exception():
                        exception = future.exception()
                        logger.error(f"_fetch_pull_request_commits: {exception}")
                        os._exit(1)

    def _dump_pull_request_events(self, number):
        logger.debug(f"Dumping Pull Request Events for Pull Request Number: {number}...")

        pr_event = EventDetailStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            since=self.start_date if not self.full else None,
            type_filter="pullRequest",
            number=number
        )

        try:
            pr_id = self.pull_requests[number]
        except KeyError:
            pr_id = self._get_table_id(table="pull_requests", field="number", value=number)
            self.pull_requests[number] = pr_id

        obj_list = self._events_object_list(pr_event, id_=pr_id, type_="PULL_REQUEST")

        self._insert(object_=self.db_schema.pull_request_events.insert(), param=obj_list)

    @timing(name="pull_request_events")
    def _fetch_pull_request_events(self):
        logger.info("Dumping Pull Request Events...")

        for prs in self.__get_pull_requests('pull_request_events'):
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                process = {executor.submit(self._dump_pull_request_events, pr): pr for pr in prs}
                for future in concurrent.futures.as_completed(process):
                    number = process[future]
                    future.result()
                    logger.debug(f"Inserted Events for PR Number: {number}")

                    if future.exception():
                        exception = future.exception()
                        logger.error(f"_fetch_pull_request_events: {exception}")
                        os._exit(1)

    def _dump_pull_request_comments(self, number):
        logger.debug(f"Dumping Pull Request Comments for Pull Request Number: {number}...")

        pr_comments = CommentStruct(
            name=self.repo_name,
            owner=self.repo_owner,
            number=number,
            type_filter="pullRequest"
        )

        try:
            pr_id = self.pull_requests[number]
        except KeyError:
            pr_id = self._get_table_id(table="pull_requests", field="number", value=number)
            self.pull_requests[number] = pr_id

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

                    if future.exception():
                        exception = future.exception()
                        logger.error(f"_fetch_pull_request_comments: {exception}")
                        os._exit(1)

    @locked
    def __check_user(self, login, name=None, email=None):
        if login:
            try:
                res = self.login_id[login]
            except KeyError:
                res = None
        else:
            try:
                res = self.name_email_id[self.Name_Email(name=name, email=email)]
            except KeyError:
                res = None

        return res

    def _get_user_id(self, login, user_object=None, name=None, email=None):
        if not login and user_object:
            res = self.__check_user(login=user_object.login)

            if not res:
                has_dumped = self._dump_user_object(login=None, user_object=user_object,
                                                    object_=self.db_schema.contributors.insert())
                if has_dumped:
                    return self._get_user_id(user_object.login)
                else:
                    return None
            else:
                return res
        elif login:
            res = self.__check_user(login=login)

            if not res:
                has_dumped = self._dump_user_object(login=login, object_=self.db_schema.contributors.insert())
                if has_dumped:
                    return self._get_user_id(login)
                else:
                    return None
            else:
                return res
        elif name and email:
            res = self.__check_user(login=None, name=name, email=email)

            if not res:
                has_dumped = self._dump_anon_user_object(name=name, email=email,
                                                         object_=self.db_schema.contributors.insert())
                if has_dumped:
                    return self._get_user_id(login=None, name=name, email=email)
                else:
                    return None
            else:
                return res
        else:
            return None

    @locked
    def __check_table(self, pk, table, field, value):
        res = self._conn.execute(
            f"""
            SELECT {pk}
            FROM {table}
            WHERE {field}="{value}" AND repo_id={self.repo_id}
            """
        ).fetchone()

        return res

    def _get_table_id(self, table, field, value, pk='id', toggle=False):
        if value is None:
            return None

        res = self.__check_table(pk, table, field, value)

        if not res:
            if table == "commits":
                if not toggle:
                    self._dump_commits(oid=value)
                    id_ = self._get_table_id(table=table, field=field, value=value, toggle=True)
                    self.commits[value] = id_
                    return id_
                else:
                    logger.debug(f"Commit oid: {value} has been deleted! Returning `None`.")
                    return None
            elif table == "issues":
                if not toggle:
                    self._dump_issues(number=value)
                    id_ = self._get_table_id(table=table, field=field, value=value, toggle=True)
                    self.issues[value] = id_
                    return id_
                else:
                    logger.debug(f"Issue number: {value} has been deleted! Returning `None`.")
                    return None
            elif table == "pull_requests":
                if not toggle:
                    self._dump_pull_requests(number=value)
            else:
                logger.error(f"pk not found for table: {table}, field: {field}, value: {value}.")
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
            SELECT DISTINCT oid, id
            FROM commits
            WHERE id NOT IN (
                SELECT DISTINCT commit_id
                FROM code_change
            )       
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
