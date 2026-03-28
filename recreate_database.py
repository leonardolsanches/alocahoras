"""
Script para recriar estrutura completa do banco PostgreSQL
com dados autênticos da planilha Excel
"""
import pandas as pd
import psycopg2
import os
from datetime import datetime

def recreate_database():
    """Recria toda estrutura do banco com dados da planilha"""
    try:
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        print("Recriando estrutura do banco...")
        
        # Criar tabela dados_planilha
        cur.execute("""
            DROP TABLE IF EXISTS dados_planilha CASCADE;
            CREATE TABLE dados_planilha (
                id SERIAL PRIMARY KEY,
                colaboradores VARCHAR(255),
                gestor_direto VARCHAR(255),
                tipo_alocacao VARCHAR(255),
                projetos VARCHAR(255),
                atividades VARCHAR(255),
                jan VARCHAR(10),
                fev VARCHAR(10),
                mar VARCHAR(10),
                abr VARCHAR(10),
                mai VARCHAR(10),
                jun VARCHAR(10),
                jul VARCHAR(10),
                ago VARCHAR(10),
                set VARCHAR(10),
                out VARCHAR(10),
                nov VARCHAR(10),
                dez VARCHAR(10)
            );
        """)
        
        # Criar tabela approval_status
        cur.execute("""
            DROP TABLE IF EXISTS approval_status CASCADE;
            CREATE TABLE approval_status (
                id SERIAL PRIMARY KEY,
                manager_name VARCHAR(255),
                collaborator_name VARCHAR(255),
                month VARCHAR(10),
                status VARCHAR(50) DEFAULT 'pendente',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Carregar dados da planilha Excel
        df = pd.read_excel('attached_assets/dados.xlsx', sheet_name='ALOCACAO')
        
        print(f"Carregando {len(df)} registros da planilha...")
        
        # Inserir dados na tabela
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO dados_planilha (
                    colaboradores, gestor_direto, tipo_alocacao, projetos, atividades,
                    jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(row['COLABORADORES']).strip(),
                str(row['GESTOR DIRETO']).strip(),
                str(row['TIPO ALOCACAO']).strip(),
                str(row['PROJETOS']).strip(),
                str(row['ATIVIDADES']).strip(),
                str(row['JAN']) if pd.notna(row['JAN']) else '0',
                str(row['FEV']) if pd.notna(row['FEV']) else '0',
                str(row['MAR']) if pd.notna(row['MAR']) else '0',
                str(row['ABR']) if pd.notna(row['ABR']) else '0',
                str(row['MAI']) if pd.notna(row['MAI']) else '0',
                str(row['JUN']) if pd.notna(row['JUN']) else '0',
                str(row['JUL']) if pd.notna(row['JUL']) else '0',
                str(row['AGO']) if pd.notna(row['AGO']) else '0',
                str(row['SET']) if pd.notna(row['SET']) else '0',
                str(row['OUT']) if pd.notna(row['OUT']) else '0',
                str(row['NOV']) if pd.notna(row['NOV']) else '0',
                str(row['DEZ']) if pd.notna(row['DEZ']) else '0'
            ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Banco recriado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recriar banco: {e}")
        return False

if __name__ == "__main__":
    recreate_database()