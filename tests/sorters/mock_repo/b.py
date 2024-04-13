from tests.sorters.mock_repo.a import DummyDataclass


def dummy_process(x):
    d = DummyDataclass(prefix=":", suffix=":")

    def inner():
        return d

    return inner
