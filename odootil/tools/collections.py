class Prefix(str):
    """String wrapper to check if string prefix is a match."""

    def __eq__(self, other):
        if isinstance(other, str):
            return other.startswith(self)
        return NotImplemented

    def __hash__(self):
        return hash(str(self))


class PrefixSet(set):
    """Set wrapper to be able to compare prefix strings in sets."""

    def __eq__(self, other):
        if not isinstance(other, (set, PrefixSet)):
            return NotImplemented
        return (
            len(self) == len(other)
            # We only care that prefixes will match, not the length.
            and all(any(s == o for o in other) for s in self)
        )
