# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import bcrypt
import os
app = Flask(__name__)

app.secret_key = os.urandom(24) 
#chave secreta é necessária para usar 'flash'

DB_NAME = 'users_db'
DB_USER = 'postgres'
DB_PASSWORD = '123321'
DB_HOST = 'localhost'
DB_PORT = '5432'
MAX_TENTATIVAS = 5


def get_db_connection():
    #conecta ao PostgreSQL e retorna a conexão
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao BD: {e}")
        return None

def criar_usuario(usuario, senha, email):
    salt = bcrypt.gensalt()
    hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), salt)
    hashed_email = bcrypt.hashpw(email.encode('utf-8'), salt) 
    categoria = 1 

    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (usuario, senha_hash, email_hash, categoria)
            VALUES (%s, %s, %s, %s)
        ''', (usuario, hashed_senha.decode('utf-8'), hashed_email.decode('utf-8'), categoria))
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        flash("Erro: Nome de usuário ou e-mail já existe.", 'error')
        return False
    except Exception as e:
        flash(f"Erro inesperado: {e}", 'error')
        return False
    finally:
        conn.close()

#rotas do servidor web

@app.route('/')
def home():
    """Carrega a página de login (index.html)."""
    #função render_template procura por 'index.html' na pasta 'templates'
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def login():

    email_ou_usuario = request.form.get('email')
    senha = request.form.get('senha')
    usuario_bd = email_ou_usuario 
    categoria_bd = 1

    conn = get_db_connection()
    if conn is None:
        return "Erro de conexão com o banco de dados.", 500

    cursor = conn.cursor()
    
    #lógica de verificação adaptada:
    cursor.execute('''
        SELECT senha_hash, tentativas_falhas, bloqueio
        FROM users
        WHERE usuario = %s AND categoria = %s
    ''', (usuario_bd, categoria_bd))
    result = cursor.fetchone()

    if not result:
        conn.close()
        flash("Usuário não encontrado ou categoria incorreta.", 'error')
        return redirect(url_for('home'))

    stored_hash, tentativas_falhas, bloqueio = result

    if bloqueio:
        conn.close()
        flash("Conta bloqueada devido a múltiplas tentativas de login falhas.", 'error')
        return redirect(url_for('home'))

    if bcrypt.checkpw(senha.encode('utf-8'), stored_hash.encode('utf-8')):
        # Login bem-sucedido
        cursor.execute('UPDATE users SET tentativas_falhas = 0 WHERE usuario = %s', (usuario_bd,))
        conn.commit()
        conn.close()
        return "<h1>🔓 Login bem-sucedido! Bem-vindo!</h1>"
    else:
        # Senha incorreta
        tentativas_falhas += 1
        
        if tentativas_falhas >= MAX_TENTATIVAS:
            cursor.execute('''
                UPDATE users
                SET tentativas_falhas = %s, bloqueio = TRUE
                WHERE usuario = %s
            ''', (tentativas_falhas, usuario_bd))
            flash("🚫 Conta bloqueada após 5 tentativas incorretas.", 'error')
        else:
            cursor.execute('UPDATE users SET tentativas_falhas = %s WHERE usuario = %s', (tentativas_falhas, usuario_bd))
            restantes = MAX_TENTATIVAS - tentativas_falhas
            flash(f"❌ Senha incorreta. Tentativas restantes: {restantes}", 'warning')

        conn.commit()
        conn.close()
        return redirect(url_for('home'))


@app.route('/cadastro', methods=['GET', 'POST'])
def tela_cadastro():
    """Rota para a tela e o processamento do cadastro."""
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')

        if senha != confirma_senha:
            flash("As senhas não coincidem.", 'error')
            return redirect(url_for('cadastro'))

        if criar_usuario(usuario, senha, email):
            flash("✅ Usuário criado com sucesso. Faça login!", 'success')
            return redirect(url_for('home'))
        else:
            # A mensagem de erro já é tratada dentro de criar_usuario com flash
            return redirect(url_for('tela_cadastro'))

    #exibe o formulário
    return render_template('cadastro.html')

@app.route('/esqueci')
def esqueci_senha():
    return render_template('esqueci.html')

@app.route('/proximo')
def proximo():
    return render_template('proximo.html')


if __name__ == '__main__':
    app.run(debug=True)