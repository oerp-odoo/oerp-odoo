class Prefix(str):
    """String wrapper to check if string prefix is a match."""

    def __eq__(self, other):
        """Match if other starts with this prefix."""
        if isinstance(other, str):
            return other.startswith(self)
        return NotImplemented

    def __hash__(self):
        """Hash as plain string to keep set/dict lookups consistent."""
        return hash(str(self))


class PrefixSet(set):
    """Set wrapper to be able to compare prefix strings in sets."""

    def __eq__(self, other):
        """Compare sets, treating Prefix items as prefix matches."""
        if not isinstance(other, (set, PrefixSet)):
            return NotImplemented
        return (
            len(self) == len(other)
            # We only care that prefixes will match, not the length.
            and all(any(s == o for o in other) for s in self)
        )
