import os
import pytest
from datetime import time

from sport_systems import stats


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture
def response_1():
    path = os.path.join(BASE_DIR, 'response-1.xml')
    with open(path, 'rb') as fin:
        data = fin.read()
    return data


@pytest.fixture
def results_1():
    return [
        stats.Result(time=time(1, 10, 15), name='foo'),
        stats.Result(time=time(1, 10, 20), name='foo'),
        stats.Result(time=time(1, 20), name='foo'),
        stats.Result(time=time(1, 30, 10), name='foo'),
        stats.Result(time=time(1, 30, 15), name='foo'),
        stats.Result(time=time(1, 30, 20), name='foo'),
    ]
