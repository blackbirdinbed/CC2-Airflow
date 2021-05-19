import sys
sys.path.append('../../src/v2/')

import pytest
import apiv2

@pytest.fixture
def client():
    apiv2.app.config['TESTING'] = True
    client = apiv2.app.test_client()

    yield client

def test_status(client):
    rv = client.get('/')
    json_data = rv.get_json()
    assert json_data['status']=="OK" and rv.status_code == 200