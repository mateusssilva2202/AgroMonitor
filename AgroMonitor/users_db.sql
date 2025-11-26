CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    usuario TEXT UNIQUE NOT NULL,
    email_hash TEXT UNIQUE NOT NULL,
    categoria INTEGER NOT NULL,
    senha_hash TEXT NOT NULL,
    tentativas_falhas INTEGER DEFAULT 0,
    bloqueio BOOLEAN DEFAULT FALSE
);