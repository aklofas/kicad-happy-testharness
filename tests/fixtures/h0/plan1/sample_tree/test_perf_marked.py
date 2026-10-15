import pytest

def test_cheap():
    assert True

@pytest.mark.perf
def test_slow_bound():
    assert True
