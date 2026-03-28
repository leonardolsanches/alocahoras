import os
import psycopg2
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from app import app, login_manager
from models import User

# Forçar DATABASE_URL para debug
os.environ['DATABASE_URL'] = "postgresql://neondb_owner:npg_v5buj1ETdLIP@ep-still-tree-ac1q7wl0-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id, name=user_id, email="", profile_type="manager")

@app.route('/')
def index():
    if not current_user.is_authenticated:
        # Login automático para evitar loading infinito
        user = User(id="admin", name="Administrador", email="admin@claro.com", profile_type="manager")
        login_user(user)
    return redirect(url_for('aprovacao'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        selected_user = request.form.get('selected_user')
        password = request.form.get('password', '').strip()
        
        if password != 'claro123':
            flash("Senha incorreta. Use: claro123", "error")
            return redirect(url_for('login'))
        
        if selected_user:
            user = User(
                id=selected_user,
                name=selected_user,
                email="",
                profile_type="manager"
            )
            login_user(user)
            return redirect(url_for('aprovacao'))
    
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT colaboradores 
            FROM dados_planilha 
            WHERE colaboradores IS NOT NULL 
            ORDER BY colaboradores
        """)
        
        managers = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return render_template('login.html', managers=managers)
    except Exception as e:
        return render_template('login.html', managers=['ALINE JULIANA LOPES'], error=str(e))

@app.route('/aprovacao')
@login_required
def aprovacao():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = conn.cursor()
        
        manager_name = current_user.name
        
        # Buscar subordinados do gestor logado
        cursor.execute("""
            SELECT DISTINCT colaboradores
            FROM dados_planilha 
            WHERE gestor_direto = %s
            AND colaboradores IS NOT NULL
            AND colaboradores NOT LIKE 'TERCEIRO%%'
            ORDER BY colaboradores
        """, (manager_name,))
        
        subordinates_raw = cursor.fetchall()
        
        subordinates = []
        for row in subordinates_raw:
            if not row or len(row) == 0:
                continue
            subordinate_name = row[0]
            
            # Buscar dados reais de alocação mensal para este colaborador
            cursor.execute("""
                SELECT jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez
                FROM dados_planilha
                WHERE colaboradores = %s
                LIMIT 1
            """, (subordinate_name,))
            
            result = cursor.fetchone()
            if result and len(result) >= 12:
                # Usar dados exatamente como estão no banco
                monthly_data = {
                    'jan': result[0] if result[0] is not None else 0,
                    'fev': result[1] if result[1] is not None else 0,
                    'mar': result[2] if result[2] is not None else 0,
                    'abr': result[3] if result[3] is not None else 0,
                    'mai': result[4] if result[4] is not None else 0,
                    'jun': result[5] if result[5] is not None else 0,
                    'jul': result[6] if result[6] is not None else 0,
                    'ago': result[7] if result[7] is not None else 0,
                    'set': result[8] if result[8] is not None else 0,
                    'out': result[9] if result[9] is not None else 0,
                    'nov': result[10] if result[10] is not None else 0,
                    'dez': result[11] if result[11] is not None else 0
                }
                
                # Buscar status de aprovação para este colaborador
                cursor.execute("""
                    SELECT month, status FROM approval_status
                    WHERE manager_name = %s AND collaborator_name = %s
                """, (manager_name, subordinate_name))
                
                approval_statuses = dict(cursor.fetchall())
                
                subordinates.append({
                    'name': subordinate_name,
                    'monthly_allocations': monthly_data,
                    'approval_statuses': approval_statuses
                })
        
        cursor.close()
        conn.close()
        
        return render_template('aprovacao.html', 
                             subordinates=subordinates,
                             manager_name=manager_name)
        
    except Exception as e:
        return render_template('aprovacao.html', 
                             subordinates=[], 
                             error=f"Erro ao carregar dados: {str(e)}",
                             manager_name=getattr(current_user, 'name', 'Usuário'))

@app.route('/api/approve-cells', methods=['POST'])
def api_approve_cells():
    try:
        data = request.get_json()
        dates = data.get('dates', [])
        status = data.get('status', 'aprovado')
        user_id = data.get('user_id', current_user.id)
        
        if not dates:
            return jsonify({"success": False, "message": "Nenhuma data enviada"})
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = conn.cursor()
        
        processed_count = 0
        manager_name = getattr(current_user, 'name', 'USUARIO_TESTE')
        print(f"[DEBUG] Manager atual: {manager_name}")
        
        # Processar TODAS as datas do array (incluindo meses diferentes)
        print(f"[DEBUG] Recebidas {len(dates)} datas para processar: {dates}")
        
        for date_str in dates:
            try:
                print(f"[DEBUG] Processando data: {date_str}")
                
                # Extrair ano e mês da data (formato: YYYY-MM-DD)
                year, month, day = date_str.split('-')
                month_key = f"{year}-{month.zfill(2)}"
                
                # Criar/atualizar registro de aprovação para cada data
                cursor.execute("""
                    INSERT INTO calendar_approvals (date, status, manager_id, approved_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (date, manager_id)
                    DO UPDATE SET 
                        status = EXCLUDED.status,
                        approved_at = CURRENT_TIMESTAMP
                """, (date_str, status, manager_name))
                
                processed_count += 1
                print(f"[DEBUG] Data {date_str} processada com sucesso. Total: {processed_count}")
                
            except Exception as date_error:
                print(f"[ERRO] Erro ao processar data {date_str}: {date_error}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True, 
            "count": processed_count,
            "message": f"{processed_count} dias processados com sucesso"
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Erro ao processar aprovação: {str(e)}"})

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/calendario')
def calendario():
    # Usar gestor real do banco de dados
    return render_template('calendario.html', current_user=current_user)

@app.route('/lancamento')
@login_required
def lancamento():
    return render_template('lancamento.html')

@app.route('/api/collaborator-details/<collaborator_name>')
@login_required
def api_collaborator_details(collaborator_name):
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Verificar se colaborador existe
        cur.execute("SELECT COUNT(*) FROM dados_planilha WHERE colaboradores = %s", (collaborator_name,))
        result = cur.fetchone()
        count = result[0] if result else 0
        
        if count == 0:
            return jsonify({
                'success': False,
                'error': f'Colaborador "{collaborator_name}" não encontrado'
            })
        
        # Buscar dados completos com percentuais mensais
        query = """
        SELECT 
            COALESCE(tipo_alocacao, 'Não especificado') as tipo_alocacao,
            COALESCE(projetos, 'Projeto não definido') as projetos,
            COALESCE(atividades, 'Atividade não definida') as atividades,
            jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez
        FROM dados_planilha 
        WHERE colaboradores = %s 
        AND tipo_alocacao IS NOT NULL 
        AND projetos IS NOT NULL 
        AND atividades IS NOT NULL
        ORDER BY tipo_alocacao, projetos, atividades
        """
        
        cur.execute(query, (collaborator_name,))
        results = cur.fetchall()
        
        # Processar dados para estrutura hierárquica com cálculos
        projects_data = {}
        
        for row in results:
            tipo_alocacao = row[0]
            projeto = row[1]
            atividade = row[2]
            
            # Converter valores mensais para float, tratando strings e valores nulos
            monthly_values = []
            for i in range(3, 15):  # jan a dez
                value = row[i]
                if value is None or value == '':
                    monthly_values.append(0.0)
                else:
                    try:
                        # Converter para float, removendo % se existir
                        if isinstance(value, str):
                            value = value.replace('%', '').strip()
                        monthly_values.append(float(value))
                    except (ValueError, TypeError):
                        monthly_values.append(0.0)
            
            project_key = f"{tipo_alocacao}|{projeto}"
            
            if project_key not in projects_data:
                projects_data[project_key] = {
                    'tipo_alocacao': tipo_alocacao,
                    'projetos': projeto,
                    'atividades': [],
                    'monthly_totals': [0.0] * 12
                }
            
            # Adicionar atividade com seus valores mensais
            projects_data[project_key]['atividades'].append({
                'nome': atividade,
                'monthly_values': monthly_values
            })
            
            # Somar valores mensais do projeto
            for i in range(12):
                projects_data[project_key]['monthly_totals'][i] += monthly_values[i]
        
        details = list(projects_data.values())
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'details': details
        })
        
    except Exception as e:
        print(f"Erro ao buscar detalhes do colaborador: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analytics-data')
@login_required
def api_analytics_data():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Buscar contagem de projetos únicos
        cur.execute("SELECT COUNT(DISTINCT projetos) FROM dados_planilha WHERE projetos IS NOT NULL AND projetos != ''")
        result = cur.fetchone()
        projects_count = result[0] if result else 0
        
        # Buscar contagem de atividades únicas
        cur.execute("SELECT COUNT(DISTINCT atividades) FROM dados_planilha WHERE atividades IS NOT NULL AND atividades != ''")
        result = cur.fetchone()
        activities_count = result[0] if result else 0
        
        # Buscar contagens de status de aprovação
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END), 0) as approved,
                COALESCE(SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END), 0) as pending,
                COALESCE(SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END), 0) as rejected
            FROM approval_status
        """)
        status_counts = cur.fetchone()
        
        # Buscar listas para filtros
        cur.execute('SELECT DISTINCT tipo_alocacao FROM dados_planilha WHERE tipo_alocacao IS NOT NULL')
        allocation_types = [row[0] for row in cur.fetchall()]
        
        cur.execute('SELECT DISTINCT projetos FROM dados_planilha WHERE projetos IS NOT NULL')
        projects = [row[0] for row in cur.fetchall()]
        
        cur.execute('SELECT DISTINCT atividades FROM dados_planilha WHERE atividades IS NOT NULL')
        activities = [row[0] for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'analytics': {
                'projects_count': projects_count,
                'activities_count': activities_count,
                'approved_count': status_counts[0] if status_counts else 0,
                'pending_count': status_counts[1] if status_counts else 0,
                'rejected_count': status_counts[2] if status_counts else 0
            },
            'filters': {
                'allocation_types': allocation_types,
                'projects': projects,
                'activities': activities
            }
        })
        
    except Exception as e:
        print(f"Erro ao buscar dados analíticos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/api/user-allocations')
def api_user_allocations():
    """API para carregar alocações existentes do usuário no calendário"""
    try:
        user_name = request.args.get('user', 'ANDRE LUIS LINS RAMOS')
        month = request.args.get('month', '1')
        year = request.args.get('year', '2025')
        
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Mapear mês para coluna
        month_names = {
            '1': 'jan', '2': 'fev', '3': 'mar', '4': 'abr',
            '5': 'mai', '6': 'jun', '7': 'jul', '8': 'ago',
            '9': 'set', '10': 'out', '11': 'nov', '12': 'dez'
        }
        
        month_col = month_names.get(month, 'jan')
        
        query = f"""
        SELECT projetos, {month_col} as percentual
        FROM dados_planilha 
        WHERE colaboradores = %s AND {month_col} IS NOT NULL AND {month_col} != ''
        """
        
        cur.execute(query, (user_name,))
        allocations = cur.fetchall()
        
        # Formatar dados por dia
        daily_allocations = {}
        import calendar as cal
        year_int = int(year)
        month_int = int(month)
        days_in_month = cal.monthrange(year_int, month_int)[1]
        
        for projeto, percentual in allocations:
            if percentual and str(percentual).strip() and percentual != '0':
                # Primeiro nome do projeto
                primeiro_nome = projeto.split()[0] if projeto else ''
                
                # Limpar percentual (remover % se existir)
                percentual_limpo = str(percentual).replace('%', '').strip()
                
                # Aplicar a todos os dias do mês
                for day in range(1, days_in_month + 1):
                    day_key = f"{year}-{month:0>2}-{day:0>2}"
                    if day_key not in daily_allocations:
                        daily_allocations[day_key] = []
                    
                    daily_allocations[day_key].append({
                        'projeto': primeiro_nome,
                        'percentual': percentual_limpo
                    })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'allocations': daily_allocations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'allocations': {}
        })

@app.route('/api/calendar-filters')
def api_calendar_filters():
    """API para carregar filtros reais do banco para o calendário"""
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cur = conn.cursor()
        
        # Buscar colaboradores únicos
        cur.execute("SELECT DISTINCT colaboradores FROM dados_planilha WHERE colaboradores IS NOT NULL ORDER BY colaboradores")
        colaboradores = [row[0] for row in cur.fetchall()]
        
        # Buscar projetos únicos
        cur.execute("SELECT DISTINCT projetos FROM dados_planilha WHERE projetos IS NOT NULL ORDER BY projetos")
        projetos = [row[0] for row in cur.fetchall()]
        
        # Buscar atividades únicas
        cur.execute("SELECT DISTINCT atividades FROM dados_planilha WHERE atividades IS NOT NULL ORDER BY atividades")
        atividades = [row[0] for row in cur.fetchall()]
        
        # Buscar tipos únicos
        cur.execute("SELECT DISTINCT tipo_alocacao FROM dados_planilha WHERE tipo_alocacao IS NOT NULL ORDER BY tipo_alocacao")
        tipos = [row[0] for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'projects': projetos,
            'activities': atividades,
            'types': tipos,
            'colaboradores': colaboradores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar-data')
def api_calendar_data():
    """API para carregar dados reais do calendário por período"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        colaborador = request.args.get('colaborador', '')
        projeto = request.args.get('projeto', '')
        atividade = request.args.get('atividade', '')
        tipo = request.args.get('tipo', '')
        
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cur = conn.cursor()
        
        # Construir query com filtros
        query = """
            SELECT colaboradores, projetos, atividades, tipo_alocacao, 
                   jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez
            FROM dados_planilha 
            WHERE 1=1
        """
        params = []
        
        if colaborador:
            query += " AND colaboradores ILIKE %s"
            params.append(f"%{colaborador}%")
        if projeto:
            query += " AND projetos ILIKE %s"
            params.append(f"%{projeto}%")
        if atividade:
            query += " AND atividades ILIKE %s"
            params.append(f"%{atividade}%")
        if tipo:
            query += " AND tipo_alocacao ILIKE %s"
            params.append(f"%{tipo}%")
            
        cur.execute(query, params)
        rows = cur.fetchall()
        
        calendar_data = []
        for row in rows:
            colaboradores, projetos, atividades, tipo_alocacao = row[:4]
            months = row[4:16]  # jan até dez
            status = 'pendente'  # Status padrão
            
            for i, month_val in enumerate(months):
                if month_val:
                    try:
                        # Converter valores percentuais (ex: "100%") para float
                        if isinstance(month_val, str) and month_val.endswith('%'):
                            valor = float(month_val.replace('%', ''))
                        else:
                            valor = float(month_val)
                        
                        if valor > 0:
                            calendar_data.append({
                                'colaborador': colaboradores,
                                'projeto': projetos,
                                'atividade': atividades,
                                'tipo': tipo_alocacao,
                                'mes': i + 1,  # 1-12
                                'valor': valor,
                                'status': status or 'pendente'
                            })
                    except (ValueError, TypeError):
                        # Ignorar valores que não podem ser convertidos
                        continue
        
        cur.close()
        conn.close()
        
        return jsonify(calendar_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hierarquia-teste')
def hierarquia_teste():
    return render_template('hierarquia_teste.html')

@app.route('/api/hierarchy-data')
def hierarchy_data():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = conn.cursor()
        
        # Buscar dados reais da planilha para hierarquia
        cursor.execute("""
            SELECT DISTINCT 
                colaboradores,
                tipo_alocacao,
                projetos,
                atividades,
                gestor_direto
            FROM dados_planilha 
            WHERE colaboradores IS NOT NULL
            AND tipo_alocacao IS NOT NULL
            AND projetos IS NOT NULL
            AND atividades IS NOT NULL
            ORDER BY colaboradores, projetos, atividades
            LIMIT 50
        """)
        
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append({
                'collaborator': row[0],
                'type': row[1],
                'project': row[2],
                'activity': row[3],
                'manager': row[4]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'data': data, 'total': len(data)})
        
    except Exception as e:
        return jsonify({'error': str(e), 'data': [], 'total': 0})