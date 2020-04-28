class RepositoryModel:
    def __init__(
        self,
        created_at,
        updated_at,
        disk_usage,
        url,
        owner_login,
        name,
        description,
        fork_count,
        homepage_url,
        is_archived,
        is_fork,
        primary_language,
        stargazer_count,
        watcher_count,
    ):
        self.name = name
        self.description = description
        self.fork_count = fork_count
        self.owner_login = owner_login
        self.url = url
        self.watcher_count = watcher_count
        self.stargazer_count = stargazer_count
        self.primary_language = primary_language
        self.is_fork = is_fork
        self.is_archived = is_archived
        self.homepage_url = homepage_url
        self.disk_usage = disk_usage
        self.updated_at = updated_at
        self.created_at = created_at


class MilestoneModel:
    def __init__(
        self,
        closed_at,
        created_at,
        creator_login,
        description,
        due_on,
        state,
        title,
        updated_at,
        number,
    ):
        self.number = number
        self.title = title
        self.state = state
        self.due_on = due_on
        self.description = description
        self.creator_login = creator_login
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at


class StargazerModel:
    def __init__(self, login, starred_at):
        self.login = login
        self.starred_at = starred_at


class LabelModel:
    def __init__(self, color, name, created_at):
        self.color = color
        self.name = name
        self.created_at = created_at


class BranchModel:
    def __init__(self, name, commit_id):
        self.commit_id = commit_id
        self.name = name


class WatcherModel:
    def __init__(self, login, created_at):
        self.login = login
        self.created_at = created_at


class LanguageModel:
    def __init__(self, language, size):
        self.language = language
        self.size = size
