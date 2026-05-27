from flask import Flask, request, jsonify, g
import sqlite3
import time
from datetime import datetime
import os
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt
)

DB_PATH = os.environ.get('KUDOS_DB_PATH', "d:/projects/Forage/Datacom/apps/api/kudos.db")

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'dev-jwt-secret'
jwt = JWTManager(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL DEFAULT 'employee',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS kudos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        recipient_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_visible INTEGER DEFAULT 1,
        moderated_by INTEGER,
        moderated_at TIMESTAMP,
        reason_for_moderation TEXT,
        deleted_at TIMESTAMP
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS kudos_moderation_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kudos_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        moderated_by INTEGER NOT NULL,
        reason TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    db.commit()

    # Seed sample users if not present
    cur.execute("SELECT count(1) as c FROM users")
    if cur.fetchone()[0] == 0:
        users = [
            ("Alice Example", "alice@example.com", "employee"),
            ("Bob Admin", "bob@example.com", "admin"),
            ("Carol User", "carol@example.com", "employee"),
        ]
        cur.executemany("INSERT OR IGNORE INTO users (display_name, email, role) VALUES (?,?,?)", users)
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_first_request
def startup():
    init_db()

def find_user_by_email(email):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cur.fetchone()


@app.route('/api/auth/login', methods=['POST'])
def login():
    payload = request.get_json() or {}
    email = payload.get('email')
    if not email:
        return jsonify({'error': 'email required'}), 400
    user = find_user_by_email(email)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    additional_claims = {'role': user['role']}
    token = create_access_token(identity=str(user['id']), additional_claims=additional_claims)
    return jsonify({'access_token': token, 'user': {'id': user['id'], 'display_name': user['display_name'], 'email': user['email'], 'role': user['role']}})

@app.route('/api/kudos', methods=['GET'])
def get_kudos():
    limit = int(request.args.get('limit', 50))
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT k.id, k.message, k.created_at, k.is_visible, 
                   s.display_name as sender_name, s.email as sender_email,
                   r.display_name as recipient_name, r.email as recipient_email
                   FROM kudos k
                   JOIN users s ON s.id = k.sender_id
                   JOIN users r ON r.id = k.recipient_id
                   WHERE k.is_visible = 1 AND k.deleted_at IS NULL
                   ORDER BY datetime(k.created_at) DESC
                   LIMIT ?
                ''', (limit,))
    rows = cur.fetchall()
    result = [dict(row) for row in rows]
    return jsonify(result)

@app.route('/api/kudos', methods=['POST'])
def create_kudos():
    payload = request.get_json() or {}
    sender_email = payload.get('sender_email')
    recipient_email = payload.get('recipient_email')
    message = (payload.get('message') or '').strip()

    if not sender_email or not recipient_email:
        return jsonify({'error':'sender_email and recipient_email are required'}), 400
    if not message:
        return jsonify({'error':'message is required'}), 400
    if len(message) > 500:
        return jsonify({'error':'message must be 500 chars or fewer'}), 400
    if sender_email == recipient_email:
        return jsonify({'error':'cannot send kudos to yourself'}), 400

    db = get_db()
    cur = db.cursor()
    sender = find_user_by_email(sender_email)
    recipient = find_user_by_email(recipient_email)
    if not sender or not recipient:
        return jsonify({'error':'sender or recipient not found'}), 400

    # simple duplicate check: same sender, recipient, message within last 60 seconds
    cur.execute('''SELECT id FROM kudos WHERE sender_id=? AND recipient_id=? AND message=? AND
                   datetime(created_at) >= datetime('now','-1 minute')''', (sender['id'], recipient['id'], message))
    if cur.fetchone():
        return jsonify({'error':'duplicate submission detected'}), 400

    cur.execute('''INSERT INTO kudos (sender_id, recipient_id, message) VALUES (?,?,?)''', (sender['id'], recipient['id'], message))
    db.commit()
    new_id = cur.lastrowid
    cur.execute('''SELECT k.id, k.message, k.created_at, s.display_name as sender_name, r.display_name as recipient_name
                   FROM kudos k
                   JOIN users s ON s.id = k.sender_id
                   JOIN users r ON r.id = k.recipient_id
                   WHERE k.id = ?''', (new_id,))
    row = cur.fetchone()
    return jsonify(dict(row)), 201

# Admin moderation endpoints (protected by simple header key for MVP)
def require_admin_jwt():
    claims = get_jwt()
    return claims.get('role') == 'admin'

@app.route('/api/admin/kudos/<int:kudos_id>/hide', methods=['PATCH'])
@jwt_required()
def hide_kudos(kudos_id):
    if not require_admin_jwt():
        return jsonify({'error':'unauthorized'}), 403
    payload = request.get_json() or {}
    reason = payload.get('reason') or ''
    if not reason:
        return jsonify({'error':'reason required'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute('UPDATE kudos SET is_visible=0, moderated_at=CURRENT_TIMESTAMP, reason_for_moderation=? WHERE id=?', (reason, kudos_id))
    cur.execute('INSERT INTO kudos_moderation_audit (kudos_id, action, moderated_by, reason) VALUES (?,?,?,?)', (kudos_id,  'hide', 0, reason))
    db.commit()
    return jsonify({'status':'hidden'})

@app.route('/api/admin/kudos/<int:kudos_id>/delete', methods=['PATCH'])
@jwt_required()
def delete_kudos(kudos_id):
    if not require_admin_jwt():
        return jsonify({'error':'unauthorized'}), 403
    payload = request.get_json() or {}
    reason = payload.get('reason') or ''
    if not reason:
        return jsonify({'error':'reason required'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute('UPDATE kudos SET deleted_at=CURRENT_TIMESTAMP WHERE id=?', (kudos_id,))
    cur.execute('INSERT INTO kudos_moderation_audit (kudos_id, action, moderated_by, reason) VALUES (?,?,?,?)', (kudos_id, 'delete', 0, reason))
    db.commit()
    return jsonify({'status':'deleted'})

@app.route('/api/admin/kudos/<int:kudos_id>/restore', methods=['PATCH'])
@jwt_required()
def restore_kudos(kudos_id):
    if not require_admin_jwt():
        return jsonify({'error':'unauthorized'}), 403
    payload = request.get_json() or {}
    reason = payload.get('reason') or 'restored'
    db = get_db()
    cur = db.cursor()
    cur.execute('UPDATE kudos SET deleted_at=NULL, is_visible=1 WHERE id=?', (kudos_id,))
    cur.execute('INSERT INTO kudos_moderation_audit (kudos_id, action, moderated_by, reason) VALUES (?,?,?,?)', (kudos_id, 'restore', 0, reason))
    db.commit()
    return jsonify({'status':'restored'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
