"""
Script para configurar DATABASE_URL com credenciais do Neon
"""
import os
import sys

def configure_database_url():
    """Configura DATABASE_URL com credenciais do Neon"""
    print("🔧 Configuração do DATABASE_URL")
    print("=" * 50)
    print()
    
    print("Cole aqui sua string de conexão PostgreSQL do Neon:")
    print("Formato: postgresql://usuario:senha@host:porta/database?sslmode=require")
    print()
    
    # Ler input do usuário
    database_url = input("DATABASE_URL: ").strip()
    
    if not database_url:
        print("❌ DATABASE_URL não pode estar vazio")
        return False
    
    if not database_url.startswith('postgresql://'):
        print("❌ DATABASE_URL deve começar com 'postgresql://'")
        return False
    
    # Tentar conectar para validar
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ Conexão bem-sucedida: {version[:50]}...")
        cur.close()
        conn.close()
        
        # Salvar em arquivo .env
        with open('.env', 'w') as f:
            f.write(f"DATABASE_URL={database_url}\n")
        
        print("✅ DATABASE_URL configurado com sucesso!")
        print("📝 Salvo em .env para uso futuro")
        return True
        
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)[:100]}")
        return False

def test_connection():
    """Testa conexão com DATABASE_URL atual"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não configurado")
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ Conexão ativa: {version[:50]}...")
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)[:100]}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_connection()
    else:
        configure_database_url()