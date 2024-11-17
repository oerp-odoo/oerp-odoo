from __future__ import annotations

import dataclasses
from enum import Enum


class WarningType(str, Enum):
    WARNING = 'warning'
    DANGER = 'danger'


@dataclasses.dataclass(frozen=True, kw_only=True)
class PackageWarning:
    warning_type: WarningType
    message: str
