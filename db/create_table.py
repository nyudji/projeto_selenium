import psycopg2
from db.config import DB_CONFIG, TABLE_NAME

def create_table():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            Produto TEXT,
            Preço FLOAT,
            "Preço Original" FLOAT,
            Desconto FLOAT,
            "Desconto Percentual" FLOAT,
            "Categoria Luxo" TEXT,
            Classificação TEXT DEFAULT 'Sem Classificação',
            Data TEXT
        )
        """
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Tabela '{TABLE_NAME}' criada (ou já existia).")
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")

if __name__ == "__main__":
    create_table()
