"""
Script para verificar arquivos Excel disponíveis
"""
import os
import pandas as pd

def verify_excel_files():
    """Verifica se arquivos Excel estão disponíveis e legíveis"""
    print("🔍 Verificando arquivos Excel disponíveis...")
    
    excel_files = [
        'attached_assets/dados.xlsx',
        'attached_assets/Dados.xlsx',
        'attached_assets/dados simples.xlsx',
        'attached_assets/dados_completos.xlsx'
    ]
    
    found_files = []
    
    for file_path in excel_files:
        if os.path.exists(file_path):
            try:
                # Tentar ler o arquivo
                df = pd.read_excel(file_path, sheet_name=None)  # Ler todas as abas
                sheets = list(df.keys())
                
                print(f"✅ {file_path}")
                print(f"   Abas encontradas: {sheets}")
                
                # Verificar se tem aba ALOCACAO
                if 'ALOCACAO' in sheets:
                    alocacao_df = pd.read_excel(file_path, sheet_name='ALOCACAO')
                    print(f"   📊 Aba ALOCACAO: {len(alocacao_df)} registros")
                    print(f"   📋 Colunas: {list(alocacao_df.columns)[:5]}...")
                    found_files.append(file_path)
                
            except Exception as e:
                print(f"❌ {file_path}: Erro ao ler - {str(e)[:50]}")
        else:
            print(f"🚫 {file_path}: Arquivo não encontrado")
    
    if found_files:
        print(f"\n✅ {len(found_files)} arquivo(s) Excel válido(s) encontrado(s)")
        print("📝 Pronto para carregar dados no PostgreSQL!")
        return found_files[0]  # Retorna o primeiro arquivo válido
    else:
        print("\n❌ Nenhum arquivo Excel válido encontrado")
        print("📤 Você precisa fazer upload da planilha Excel na pasta attached_assets/")
        return None

if __name__ == "__main__":
    verify_excel_files()