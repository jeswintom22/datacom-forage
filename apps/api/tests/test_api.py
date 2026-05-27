import os
import tempfile
import pytest
import sqlite3
import werkzeug

if not hasattr(werkzeug, '__version__'):
    werkzeug.__version__ = '3.1.8'


@pytest.fixture
def client(tmp_path, monkeypatch):
    # prepare test DB path and point the app to it
    db_path = str(tmp_path / "test_kudos.db")
    monkeypatch.setenv('KUDOS_DB_PATH', db_path)
    # import app after env set
    from apps.api import app, init_db
    # ensure DB and seed users within app context
    with app.app_context():
        init_db()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_login_and_kudos_flow(client):
    # login as alice
    rv = client.post('/api/auth/login', json={'email': 'alice@example.com'})
    assert rv.status_code == 200
    data = rv.get_json()
    token = data['access_token']

    # create kudos from alice to carol
    payload = {'sender_email': 'alice@example.com', 'recipient_email': 'carol@example.com', 'message': 'Thanks!'}
    rv2 = client.post('/api/kudos', json=payload)
    assert rv2.status_code == 201
    kudos = rv2.get_json()
    assert kudos['message'] == 'Thanks!'

    # fetch feed
    rv3 = client.get('/api/kudos')
    assert rv3.status_code == 200
    feed = rv3.get_json()
    assert any(k['message'] == 'Thanks!' for k in feed)

def test_admin_moderation(client):
    # login as admin (bob)
    rv = client.post('/api/auth/login', json={'email': 'bob@example.com'})
    assert rv.status_code == 200
    data = rv.get_json()
    token = data['access_token']

    # create a kudos to moderate
    payload = {'sender_email': 'alice@example.com', 'recipient_email': 'carol@example.com', 'message': 'Needs hide'}
    rv2 = client.post('/api/kudos', json=payload)
    assert rv2.status_code == 201
    kudos = rv2.get_json()
    kid = kudos['id']

    # hide the kudos as admin
    rv3 = client.patch(f'/api/admin/kudos/{kid}/hide', json={'reason': 'inappropriate'}, headers={'Authorization': f'Bearer {token}'})
    assert rv3.status_code == 200
    assert rv3.get_json().get('status') == 'hidden'