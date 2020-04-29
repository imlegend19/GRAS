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


class IssueModel:
    def __init__(self, created_at, updated_at, closed_at, title, body, author_login, assignees, number,
                 milestone_number, labels, state, positive_reaction_count, negative_reaction_count,
                 ambiguous_reaction_count):
        self.ambiguous_reaction_count = ambiguous_reaction_count
        self.negative_reaction_count = negative_reaction_count
        self.positive_reaction_count = positive_reaction_count
        self.closed_at = closed_at
        self.updated_at = updated_at
        self.state = state
        self.labels = labels
        self.milestone_number = milestone_number
        self.number = number
        self.assignees = assignees
        self.author_login = author_login
        self.body = body
        self.title = title
        self.created_at = created_at


class IssueCommentModel:
    def __init__(self, author_login, author_association, body, created_at, updated_at, is_minimized, minimized_reason,
                 positive_reaction_count, negative_reaction_count, ambiguous_reaction_count):
        self.updated_at = updated_at
        self.author_login = author_login
        self.author_association = author_association
        self.body = body
        self.created_at = created_at
        self.is_minimized = is_minimized
        self.minimized_reason = minimized_reason
        self.positive_reaction_count = positive_reaction_count
        self.negative_reaction_count = negative_reaction_count
        self.ambiguous_reaction_count = ambiguous_reaction_count
