import os
import sys
sys.path.append(os.getcwd())
os.environ['KUDOS_DB_PATH'] = 'd:/projects/Forage/Datacom/apps/api/kudos_test_debug.db'
from apps.api import app, init_db
# debug script; relies on pinned Werkzeug in requirements
with app.app_context():
    init_db()

with app.test_client() as c:
    rv = c.post('/api/auth/login', json={'email':'bob@example.com'})
    print('login', rv.status_code, rv.get_json())
    token = rv.get_json().get('access_token')
    rv2 = c.post('/api/kudos', json={'sender_email':'alice@example.com','recipient_email':'carol@example.com','message':'Debug hide'})
    print('create', rv2.status_code, rv2.get_json())
    kid = rv2.get_json().get('id')
    rv3 = c.patch(f'/api/admin/kudos/{kid}/hide', json={'reason':'inappropriate'}, headers={'Authorization': f'Bearer {token}'})
    print('hide', rv3.status_code, rv3.get_json(), rv3.data)
