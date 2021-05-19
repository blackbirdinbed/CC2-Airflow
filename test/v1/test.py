import sys
sys.path.append('../src/v1/')

import os
import tempfile

import pytest
import v1

@pytest.fixture
def client():
    v1.app.config['TESTING'] = True
    client = v1.app.test_client()

    yield client

def test_status(client):
    rv = client.get('/')
    json_data = rv.get_json()
    assert json_data['status']=="OK" and rv.status_code == 200