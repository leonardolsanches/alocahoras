"""
Script para carregar dados da planilha Excel no PostgreSQL
Execute após criar as tabelas com neon_database_setup.sql
"""
import pandas as pd
import psycopg2
import os
from datetime import datetime

def load_excel_to_postgres(database_url):
    """
    Carrega dados autênticos da planilha Excel para PostgreSQL
    
    Args:
        database_url: String de conexão PostgreSQL do Neon
    """
    try:
        print("🚀 Iniciando carregamento dos dados da planilha Excel...")
        
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Verificar se tabelas existem
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'dados_planilha'
        """)
        
        if not cur.fetchone():
            print("❌ Erro: Tabela 'dados_planilha' não encontrada!")
            print("Execute primeiro o script neon_database_setup.sql")
            return False
        
        # Limpar dados existentes
        cur.execute("DELETE FROM dados_planilha")
        cur.execute("DELETE FROM approval_status")
        print("🧹 Dados existentes removidos")
        
        # Carregar planilha Excel
        excel_files = ['attached_assets/dados.xlsx', 'attached_assets/Dados.xlsx']
        df = None
        
        for excel_file in excel_files:
            if os.path.exists(excel_file):
                try:
                    df = pd.read_excel(excel_file, sheet_name='ALOCACAO')
                    print(f"📊 Planilha carregada: {excel_file} ({len(df)} registros)")
                    break
                except Exception as e:
                    print(f"⚠️ Erro ao ler {excel_file}: {e}")
                    continue
        
        if df is None:
            print("❌ Erro: Planilha Excel não encontrada!")
            return False
        
        # Processar e inserir dados
        records_inserted = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # Limpar dados
                colaborador = str(row['COLABORADORES']).strip()
                gestor = str(row['GESTOR DIRETO']).strip()
                tipo = str(row['TIPO ALOCACAO']).strip()
                projeto = str(row['PROJETOS']).strip()
                atividade = str(row['ATIVIDADES']).strip()
                
                # Pular registros inválidos
                if colaborador in ['nan', 'NaN', ''] or gestor in ['nan', 'NaN', '']:
                    continue
                
                # Preparar dados mensais
                meses = {}
                for mes in ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 
                           'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']:
                    valor = row.get(mes, '0')
                    if pd.isna(valor) or str(valor).strip() in ['', 'nan', 'NaN']:
                        meses[mes.lower()] = '0'
                    else:
                        # Remover % se existir e manter apenas números
                        valor_limpo = str(valor).replace('%', '').strip()
                        try:
                            # Validar se é número
                            float(valor_limpo)
                            meses[mes.lower()] = valor_limpo
                        except:
                            meses[mes.lower()] = '0'
                
                # Inserir registro
                cur.execute("""
                    INSERT INTO dados_planilha (
                        colaboradores, gestor_direto, tipo_alocacao, projetos, atividades,
                        jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    colaborador, gestor, tipo, projeto, atividade,
                    meses['jan'], meses['fev'], meses['mar'], meses['abr'],
                    meses['mai'], meses['jun'], meses['jul'], meses['ago'],
                    meses['set'], meses['out'], meses['nov'], meses['dez']
                ))
                
                records_inserted += 1
                
                # Commit a cada 100 registros
                if records_inserted % 100 == 0:
                    conn.commit()
                    print(f"📝 {records_inserted} registros inseridos...")
                
            except Exception as e:
                errors += 1
                print(f"⚠️ Erro na linha {idx + 1}: {str(e)[:100]}")
                continue
        
        # Commit final
        conn.commit()
        
        # Verificar resultados
        cur.execute("SELECT COUNT(*) FROM dados_planilha")
        total_records = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT colaboradores) FROM dados_planilha")
        total_colaboradores = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT gestor_direto) FROM dados_planilha")
        total_gestores = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT projetos) FROM dados_planilha")
        total_projetos = cur.fetchone()[0]
        
        print("\n✅ CARREGAMENTO CONCLUÍDO!")
        print(f"📊 Total de registros: {total_records}")
        print(f"👥 Colaboradores únicos: {total_colaboradores}")
        print(f"👔 Gestores únicos: {total_gestores}")
        print(f"📁 Projetos únicos: {total_projetos}")
        print(f"❌ Erros encontrados: {errors}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def verify_data_integrity(database_url):
    """Verifica integridade dos dados carregados"""
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("\n🔍 VERIFICAÇÃO DE INTEGRIDADE")
        print("=" * 40)
        
        # Verificar alguns colaboradores específicos
        test_users = ['ANDRE LUIS LINS RAMOS', 'ADRIANO GARROTE TORRESAN', 'ALINE LUIZA CARNEIRO SANTOS']
        
        for user in test_users:
            cur.execute("""
                SELECT colaboradores, gestor_direto, jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez
                FROM dados_planilha 
                WHERE colaboradores = %s
                LIMIT 1
            """, (user,))
            
            result = cur.fetchone()
            if result:
                print(f"✅ {user}: Encontrado")
                meses_com_alocacao = sum(1 for i in range(2, 14) if result[i] and result[i] != '0')
                print(f"   └─ Meses com alocação: {meses_com_alocacao}/12")
            else:
                print(f"❌ {user}: Não encontrado")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

if __name__ == "__main__":
    # Exemplo de uso
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        success = load_excel_to_postgres(DATABASE_URL)
        if success:
            verify_data_integrity(DATABASE_URL)
    else:
        print("❌ Erro: DATABASE_URL não configurado")
        print("\nConfigure sua string de conexão PostgreSQL:")
        print("export DATABASE_URL='postgresql://usuario:senha@host:porta/banco'")