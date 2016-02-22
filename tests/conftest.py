import os
import pytest


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture
def response_1():
    path = os.path.join(BASE_DIR, 'response-1.xml')
    with open(path, 'rb') as fin:
        data = fin.read()
    return data
