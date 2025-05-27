import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "fecomdb.db"

if not DB_PATH.exists():
    raise FileNotFoundError(f"Banco de dados não encontrado: {DB_PATH.resolve()}")

def consulta_ipca_recife():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        tabela = "ipca_7060_recife"
        localidade = "Recife (PE)"
        
        query = f'''
        SELECT periodo, Valor
        FROM "{tabela}"
        WHERE Localidade = ?
        ORDER BY periodo;
        '''
        
        cursor.execute(query, (localidade,))
        resultados = cursor.fetchall()
        
        if resultados:
            print(f"IPCA para {localidade}:")
            for periodo, valor in resultados:
                print(f"- {periodo}: {valor}")
        else:
            print(f"IPCA para {localidade} (0 registros):")

if __name__ == "__main__":
    consulta_ipca_recife()
