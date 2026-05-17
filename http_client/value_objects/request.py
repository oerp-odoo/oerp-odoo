from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from ..const import HttpVerb

if TYPE_CHECKING:
    from .models.http_client_profile import HttpClientProfile


@dataclasses.dataclass(frozen=True, kw_only=True)
class RelativePath:
    """Path item representing data to generate path for URL.

    Args:
        pattern: static path or path with placeholers. Example:
            /my/path or /my/{}/path
        args: arguments to render path pattern. Only needed when path
            is with placeholders.
        params: dictionary of parameters to form query with URL.

    """

    pattern: str
    args: tuple = ()
    params: dict[str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, kw_only=True)
class RequestInput:
    method: HttpVerb
    profile: HttpClientProfile
    data_format_type: str | None = None
    data: any = None
    headers: dict[str, str] = dataclasses.field(default_factory=dict)
    options: dict = dataclasses.field(default_factory=dict)
    url: str | None = None
    relative_path: RelativePath | None = None

    def __post_init__(self):
        if (self.data is None) != (self.data_format_type is None):
            raise ValueError(
                "data and data_format_type must be used together or not at all"
            )
        if not (bool(self.url) ^ bool(self.relative_path)):
            raise ValueError("url or relative_path must be used but not both")
