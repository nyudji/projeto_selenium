import psycopg2
from db.config import DB_CONFIG

def create_database(dbname):
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',  # banco master para criar DB
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}';")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {dbname};")
            print(f"Banco de dados '{dbname}' criado com sucesso.")
        else:
            print(f"Banco de dados '{dbname}' já existe.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar banco: {e}")

if __name__ == "__main__":
    create_database(DB_CONFIG['database'])