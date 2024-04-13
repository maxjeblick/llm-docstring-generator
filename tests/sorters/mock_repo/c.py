from tests.sorters.mock_repo.b import dummy_process


def dummy_a(x):
    dummy_process(0)
    dummy_b(x - 1)


def dummy_b(x):
    if x < 0:
        return 0
    dummy_process(1)
    dummy_a(x)
