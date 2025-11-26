from psycopg2 import sql
import psycopg2

conn = psycopg2.connect(
    dbname="users_db",
    user="postgres",
    password="123321",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    usuario TEXT UNIQUE NOT NULL,
    email_hash TEXT UNIQUE NOT NULL,
    categoria INTEGER NOT NULL,
    senha_hash TEXT NOT NULL,
    tentativas_falhas INTEGER DEFAULT 0,
    bloqueio BOOLEAN DEFAULT FALSE
);
""")
conn.commit()
conn.close()
print("Banco criado!")
