import dataclasses
import enum

PFX_REPO_PATH_PATTERN = '/repos/{owner}/{name}'


class PullState(str, enum.Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    ALL = 'all'


class PullSort(str, enum.Enum):
    CREATED = 'created'
    UPDATED = 'updated'
    POPULARITY = 'popularity'
    LONG_RUNNING = 'long-running'


class SortDirection(str, enum.Enum):
    ASC = 'asc'
    DESC = 'desc'


@dataclasses.dataclass(frozen=True, kw_only=True)
class Repo:
    """Data class representing github repository.

    Args:
        name: name of the repository
        owner: github organization or github username.

    """

    name: str
    owner: str

    @property
    def pfx_path(self):
        return PFX_REPO_PATH_PATTERN.format(owner=self.owner, name=self.name)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PullParams:
    """Data to specify pull request query params.

    Args:
        state: pull request state.
        head: Filter pulls by head user or head organization and branch.
            name in the format of user:ref-name or organization:ref-name.
            For example: github:new-script-format or octocat:test-branch.
        base: Filter pulls by base branch name. Example: gh-pages
        sort: What to sort results by. popularity will sort by the
            number of comments. long-running will sort by date created
            and will limit the results to pull requests that have been
            open for more than a month and have had activity within the
            past month.
        direction: The direction of the sort. Default: desc when sort is
            created or sort is not specified, otherwise asc.
        per_page: The number of results per page (max 100).
        page: The page number of the results to fetch. For more
            information.

    """

    state: PullState = PullState.OPEN
    head: str | None = None
    base: str | None = None
    sort: PullSort = PullSort.CREATED
    direction: SortDirection | None = None
    per_page: int | None = None
    page: int | None = None
