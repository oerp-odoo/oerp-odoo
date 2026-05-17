import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProfileFilter:
    integration: str | None = None
    company_id: int | None = None
