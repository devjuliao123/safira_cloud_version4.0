from flask import Flask, request, jsonify, render_template
import psycopg2
import re
import os

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES
# =========================

DB_NAME = "homologacao_safira_softwares"

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "xbala"
}

# =========================
# CONEXÃO
# =========================

def conectar(db=DB_NAME):
    try:
        conn = psycopg2.connect(
            database=db,
            **DB_CONFIG
        )
        conn.autocommit = True
        return conn

    except Exception as e:
        print(f"Erro conexão: {e}")
        return None

# =========================
# CRIAÇÃO DO BANCO
# =========================

def criar_database():

    conn = psycopg2.connect(
        database="postgres",
        **DB_CONFIG
    )

    conn.autocommit = True

    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (DB_NAME,)
    )

    existe = cur.fetchone()

    if not existe:

        print(f"Criando banco {DB_NAME}...")

        cur.execute(
            f'CREATE DATABASE "{DB_NAME}"'
        )

        print(f"Banco {DB_NAME} criado com sucesso.")

    cur.close()
    conn.close()

# =========================
# CARREGA SQL BASE
# =========================

def carregar_sql():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    caminho_sql = os.path.join(
        base_dir,
        "schema",
        "schema_base.sql"
    )

    with open(
        caminho_sql,
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()

# =========================
# EXECUTA SQL NO SCHEMA
# =========================
def executar_schema(conn, schema):

    cur = conn.cursor()

    sql = carregar_sql()

    print(f"Schema: {schema}")
    print(f"Tamanho SQL: {len(sql)}")

    cur.execute(f'SET search_path TO "{schema}"')

    cur.execute("SHOW search_path")
    print("Search Path:", cur.fetchone())

    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name = %s
    """, (schema,))

    print("Schema existe:", cur.fetchone())

    cur.execute(sql)

    conn.commit()

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
    """, (schema,))

    tabelas = cur.fetchall()

    print("Tabelas criadas:", tabelas)

    cur.close()

# =========================
# INICIALIZA SISTEMA
# =========================

def inicializar():

    criar_database()

    conn = conectar()

    if not conn:
        return

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS public.tbl_organizacoes (
            numero INT PRIMARY KEY,
            nome TEXT NOT NULL,
            schema TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    cur.close()
    conn.close()

# =========================
# BUSCA PRÓXIMO NÚMERO
# =========================

def proximo_numero():

    conn = conectar()

    if not conn:
        return 1

    cur = conn.cursor()

    cur.execute("""
        SELECT nspname
        FROM pg_catalog.pg_namespace
        WHERE nspname LIKE 'org_%'
    """)

    schemas = cur.fetchall()

    cur.close()
    conn.close()

    maior_numero = 0

    for (nome_schema,) in schemas:

        try:

            numero_extraido = int(
                re.sub(
                    r'[^0-9]',
                    '',
                    nome_schema
                )
            )

            if numero_extraido > maior_numero:
                maior_numero = numero_extraido

        except ValueError:
            pass

    return maior_numero + 1

# =========================
# ROTAS
# =========================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/proximo-id")
def get_proximo_id():

    prox = proximo_numero()

    schema_formatado = (
        f"org_{str(prox).zfill(4)}"
    )

    return jsonify({
        "sucesso": True,
        "proximo": schema_formatado
    })

@app.route("/organizacoes")
def listar_orgs():

    conn = conectar()

    if not conn:
        return jsonify([])

    cur = conn.cursor()

    cur.execute("""
        SELECT
            numero,
            nome,
            schema
        FROM public.tbl_organizacoes
        ORDER BY numero DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    lista = []

    for r in rows:

        lista.append({
            "numero": r[0],
            "nome": r[1],
            "schema": r[2]
        })

    return jsonify(lista)

@app.route(
    "/criar-organizacao",
    methods=["POST"]
)
def criar_org():

    data = request.json

    nome = data.get("nome")

    if not nome:

        return jsonify({
            "status": "erro",
            "mensagem": "Nome é obrigatório"
        }), 400

    conn = conectar()

    if not conn:

        return jsonify({
            "status": "erro",
            "mensagem": "Erro de conexão com banco"
        }), 500

    try:

        numero = proximo_numero()

        schema = (
            f"org_{str(numero).zfill(4)}"
        )

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO public.tbl_organizacoes
            (
                numero,
                nome,
                schema
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            numero,
            nome,
            schema
        ))

        cur.execute(
            f'CREATE SCHEMA "{schema}"'
        )

        executar_schema(
            conn,
            schema
        )

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "status": "ok",
            "numero": numero,
            "schema": schema
        })

    except Exception as e:

        print("ERRO:", e)

        if conn:
            conn.close()

        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

# =========================
# START
# =========================

if __name__ == "__main__":

    inicializar()

    app.run(
        debug=True
    )