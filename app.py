import os
from flask import Flask
from flask_login import LoginManager

# Forçar DATABASE_URL para o banco Neon ativo
os.environ['DATABASE_URL'] = "postgresql://neondb_owner:npg_v5buj1ETdLIP@ep-still-tree-ac1q7wl0-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Imprimir para debug
print(f"[DEBUG] DATABASE_URL configurada: {os.environ['DATABASE_URL'][:50]}...")

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'