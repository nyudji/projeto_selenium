import psycopg2
from db.config import DB_CONFIG, TABLE_NAME

def insert_postgres(df_pandas):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_sql = f"""
        INSERT INTO {TABLE_NAME} (Produto, Preço, "Preço Original", Desconto, "Desconto Percentual", "Categoria Luxo", Classificação, Data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        data_tuples = [tuple(x) for x in df_pandas.to_numpy()]
        cursor.executemany(insert_sql, data_tuples)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"{len(df_pandas)} registros inseridos no PostgreSQL na tabela '{TABLE_NAME}'.")
    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
