-- 001_create_tables.sql: initial schema
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS migrations (
    id TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
);

CREATE TABLE IF NOT EXISTS kudos_moderation_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kudos_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    moderated_by INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
