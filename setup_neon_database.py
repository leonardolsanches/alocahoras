"""
Setup completo do banco Neon - Configure suas credenciais aqui
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# ==========================================
# CONFIGURE SUAS CREDENCIAIS DO NEON AQUI:
# ==========================================

# Cole sua string de conexão PostgreSQL do Neon aqui:
NEON_DATABASE_URL = "postgresql://neondb_owner:npg_v5buj1ETdLIP@ep-still-tree-ac1q7wl0-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Ou configure separadamente:
NEON_CONFIG = {
    "host": "seu-host.neon.tech",
    "port": 5432,
    "database": "neondb", 
    "user": "seu_usuario",
    "password": "sua_senha",
    "sslmode": "require"
}

def build_connection_string():
    """Constrói string de conexão a partir das configurações"""
    if NEON_DATABASE_URL and NEON_DATABASE_URL != "postgresql://usuario:senha@host:porta/database?sslmode=require":
        return NEON_DATABASE_URL
    
    return f"postgresql://{NEON_CONFIG['user']}:{NEON_CONFIG['password']}@{NEON_CONFIG['host']}:{NEON_CONFIG['port']}/{NEON_CONFIG['database']}?sslmode={NEON_CONFIG['sslmode']}"

def test_connection():
    """Testa conexão com o banco Neon"""
    try:
        conn_string = build_connection_string()
        print(f"🔗 Testando conexão com: {conn_string.split('@')[1].split('?')[0]}")
        
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        
        print(f"✅ Conexão bem-sucedida!")
        print(f"📊 PostgreSQL: {version[:50]}...")
        
        cur.close()
        conn.close()
        return conn_string
        
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        print("\n💡 Verifique se:")
        print("- As credenciais estão corretas")
        print("- O endpoint Neon está ativo")
        print("- A string de conexão está no formato correto")
        return None

def setup_database():
    """Configura o banco de dados completo"""
    print("🚀 Setup do Banco PostgreSQL Neon")
    print("=" * 50)
    
    # Testar conexão
    conn_string = test_connection()
    if not conn_string:
        print("\n❌ Não foi possível conectar ao banco")
        print("📝 Configure suas credenciais no arquivo setup_neon_database.py")
        return False
    
    try:
        # Configurar variável de ambiente
        os.environ['DATABASE_URL'] = conn_string
        
        # Salvar em arquivo .env
        with open('.env', 'w') as f:
            f.write(f"DATABASE_URL={conn_string}\n")
        
        print("\n✅ DATABASE_URL configurado com sucesso!")
        
        # Executar estrutura SQL
        print("\n🔧 Criando estrutura do banco...")
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        # Ler e executar script SQL
        with open('neon_database_setup.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        cur.execute(sql_script)
        conn.commit()
        
        print("✅ Estrutura do banco criada!")
        
        # Carregar dados do Excel
        print("\n📊 Carregando dados do Excel...")
        from load_excel_data import load_excel_to_postgres
        success = load_excel_to_postgres(conn_string)
        
        if success:
            print("✅ Dados carregados com sucesso!")
            print("\n🎉 Setup completo! Sistema pronto para uso.")
            return True
        else:
            print("❌ Erro ao carregar dados do Excel")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante setup: {str(e)}")
        return False

def check_current_status():
    """Verifica status atual do banco"""
    print("📊 Status Atual do Banco")
    print("=" * 30)
    
    conn_string = build_connection_string()
    
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        # Verificar tabelas
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"📋 Tabelas: {tables}")
        
        # Contar registros
        if 'dados_planilha' in tables:
            cur.execute("SELECT COUNT(*) FROM dados_planilha")
            count = cur.fetchone()[0]
            print(f"📊 Registros na dados_planilha: {count}")
        
        # Verificar colaboradores únicos
        if 'dados_planilha' in tables:
            cur.execute("SELECT COUNT(DISTINCT colaboradores) FROM dados_planilha")
            count = cur.fetchone()[0]
            print(f"👥 Colaboradores únicos: {count}")
        
        cur.close()
        conn.close()
        
        print("✅ Banco funcionando normalmente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Configurador do Banco Neon")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_connection()
        elif sys.argv[1] == "status":
            check_current_status()
        elif sys.argv[1] == "setup":
            setup_database()
    else:
        print("Comandos disponíveis:")
        print("  python setup_neon_database.py test    # Testar conexão")
        print("  python setup_neon_database.py status  # Verificar status")
        print("  python setup_neon_database.py setup   # Setup completo")
        print()
        print("⚠️  IMPORTANTE: Configure suas credenciais no arquivo antes de usar!")
        print("    Edite as variáveis NEON_DATABASE_URL ou NEON_CONFIG no topo do arquivo")