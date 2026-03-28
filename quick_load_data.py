"""
Carregamento rápido dos dados da planilha Excel
"""
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def quick_load_data():
    """Carrega dados rapidamente usando bulk insert"""
    
    # Configurar DATABASE_URL
    DATABASE_URL = "postgresql://neondb_owner:npg_v5buj1ETdLIP@ep-still-tree-ac1q7wl0-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    os.environ['DATABASE_URL'] = DATABASE_URL
    
    try:
        print("🚀 Carregamento rápido iniciado...")
        
        # Conectar
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Limpar dados existentes
        cur.execute("DELETE FROM dados_planilha")
        cur.execute("DELETE FROM approval_status")
        
        # Carregar Excel
        df = pd.read_excel('attached_assets/dados.xlsx', sheet_name='ALOCACAO')
        print(f"📊 Carregando {len(df)} registros...")
        
        # Preparar dados para bulk insert
        data_to_insert = []
        
        for idx, row in df.iterrows():
            colaborador = str(row['COLABORADORES']).strip()
            gestor = str(row['GESTOR DIRETO']).strip()
            
            if colaborador in ['nan', 'NaN', ''] or gestor in ['nan', 'NaN', '']:
                continue
                
            tipo = str(row['TIPO ALOCACAO']).strip()
            projeto = str(row['PROJETOS']).strip()
            atividade = str(row['ATIVIDADES']).strip()
            
            # Processar meses
            meses = []
            for mes in ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']:
                valor = row.get(mes, '0')
                if pd.isna(valor) or str(valor).strip() in ['', 'nan', 'NaN']:
                    meses.append('0')
                else:
                    valor_limpo = str(valor).replace('%', '').strip()
                    try:
                        float(valor_limpo)
                        meses.append(valor_limpo)
                    except:
                        meses.append('0')
            
            # Adicionar à lista
            data_to_insert.append([
                colaborador, gestor, tipo, projeto, atividade
            ] + meses)
        
        # Bulk insert
        execute_values(
            cur,
            """
            INSERT INTO dados_planilha (
                colaboradores, gestor_direto, tipo_alocacao, projetos, atividades,
                jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez
            ) VALUES %s
            """,
            data_to_insert,
            page_size=100
        )
        
        conn.commit()
        
        # Verificar resultados
        cur.execute("SELECT COUNT(*) FROM dados_planilha")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT colaboradores) FROM dados_planilha")
        colaboradores = cur.fetchone()[0]
        
        print(f"✅ Carregado: {total} registros")
        print(f"👥 Colaboradores: {colaboradores}")
        
        cur.close()
        conn.close()
        
        # Salvar DATABASE_URL no .env
        with open('.env', 'w') as f:
            f.write(f"DATABASE_URL={DATABASE_URL}\n")
        
        print("✅ DATABASE_URL configurado no .env")
        print("🎉 Sistema pronto para uso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    quick_load_data()