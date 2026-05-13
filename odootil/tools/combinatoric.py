import itertools


def powerset(iterable, include_empty=False):
    """Get all possible combinations of iterable.

    include_empty=True:
        powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    include_empty=False:
        powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    start_idx = 1
    if include_empty:
        start_idx = 0
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(start_idx, len(s) + 1)
    )
