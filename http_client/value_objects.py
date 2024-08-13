import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class PathItem:
    """Path item representing data to generate path for URL.

    Args:
        path_expression: path for URL or path pattern. Example:
            /my/path or /my/{}/path
        args: arguments to render path pattern. Only needed when path
            is pattern.
        params: dictionary of parameters to form query with URL.

    """

    path_expression: str
    args: tuple = ()
    params: dict[str] = None
