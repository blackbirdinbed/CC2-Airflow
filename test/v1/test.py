import sys
sys.path.append('../src/v1/')

import os
import tempfile

import pytest
import apiv1

@pytest.fixture
def client():
    apiv1.app.config['TESTING'] = True
    client = apiv1.app.test_client()

    yield client

def test_status(client):
    rv = client.get('/')
    json_data = rv.get_json()
    assert json_data['status']=="OK" and rv.status_code == 200