"""
Dados de fallback quando PostgreSQL não está disponível
Carrega dados do Excel diretamente para manter funcionalidade
"""
import pandas as pd
import os

def get_fallback_data():
    """Carrega dados diretamente do Excel quando PostgreSQL não está disponível"""
    try:
        # Verificar se arquivo Excel existe
        excel_path = 'attached_assets/dados.xlsx'
        if not os.path.exists(excel_path):
            return None
            
        df = pd.read_excel(excel_path, sheet_name='ALOCACAO')
        
        # Processar dados para formato necessário
        dados_processados = []
        for _, row in df.iterrows():
            colaborador = str(row['COLABORADORES']).strip()
            gestor = str(row['GESTOR DIRETO']).strip()
            
            if colaborador != 'nan' and gestor != 'nan':
                dados_processados.append({
                    'colaboradores': colaborador,
                    'gestor_direto': gestor,
                    'tipo_alocacao': str(row['TIPO ALOCACAO']).strip(),
                    'projetos': str(row['PROJETOS']).strip(),
                    'atividades': str(row['ATIVIDADES']).strip(),
                    'jan': row['JAN'] if pd.notna(row['JAN']) else '0',
                    'fev': row['FEV'] if pd.notna(row['FEV']) else '0',
                    'mar': row['MAR'] if pd.notna(row['MAR']) else '0',
                    'abr': row['ABR'] if pd.notna(row['ABR']) else '0',
                    'mai': row['MAI'] if pd.notna(row['MAI']) else '0',
                    'jun': row['JUN'] if pd.notna(row['JUN']) else '0',
                    'jul': row['JUL'] if pd.notna(row['JUL']) else '0',
                    'ago': row['AGO'] if pd.notna(row['AGO']) else '0',
                    'set': row['SET'] if pd.notna(row['SET']) else '0',
                    'out': row['OUT'] if pd.notna(row['OUT']) else '0',
                    'nov': row['NOV'] if pd.notna(row['NOV']) else '0',
                    'dez': row['DEZ'] if pd.notna(row['DEZ']) else '0'
                })
        
        return dados_processados
        
    except Exception as e:
        print(f"Erro ao carregar dados de fallback: {e}")
        return None

def get_user_allocations_fallback(user_name, month, year):
    """Busca alocações do usuário no Excel quando PostgreSQL indisponível"""
    dados = get_fallback_data()
    if not dados:
        return {"success": False, "allocations": {}}
    
    # Mapear mês para coluna
    meses = {
        '1': 'jan', '2': 'fev', '3': 'mar', '4': 'abr',
        '5': 'mai', '6': 'jun', '7': 'jul', '8': 'ago',
        '9': 'set', '10': 'out', '11': 'nov', '12': 'dez'
    }
    
    coluna_mes = meses.get(str(month), 'jan')
    
    # Buscar alocações do usuário
    alocacoes_usuario = [d for d in dados if d['colaboradores'] == user_name]
    
    if not alocacoes_usuario:
        return {"success": True, "allocations": {}}
    
    # Processar alocações por dia do mês
    allocations = {}
    
    # Obter número de dias no mês
    import calendar
    num_dias = calendar.monthrange(int(year), int(month))[1]
    
    for alocacao in alocacoes_usuario:
        percentual = str(alocacao[coluna_mes]).replace('%', '').strip()
        
        if percentual and percentual != '0':
            try:
                percentual_num = float(percentual)
                if percentual_num > 0:
                    # Adicionar para todos os dias do mês
                    for dia in range(1, num_dias + 1):
                        data_key = f"{year}-{month:02d}-{dia:02d}"
                        
                        if data_key not in allocations:
                            allocations[data_key] = []
                        
                        allocations[data_key].append({
                            'projeto': alocacao['projetos'],
                            'percentual': str(int(percentual_num))
                        })
            except:
                continue
    
    return {"success": True, "allocations": allocations}

def get_subordinates_fallback(manager_name):
    """Busca subordinados no Excel quando PostgreSQL indisponível"""
    dados = get_fallback_data()
    if not dados:
        return []
    
    # Encontrar subordinados do gestor
    subordinados = {}
    for d in dados:
        if d['gestor_direto'] == manager_name:
            nome_colaborador = d['colaboradores']
            if nome_colaborador not in subordinados:
                subordinados[nome_colaborador] = {
                    'name': nome_colaborador,
                    'monthly_allocations': {
                        'jan': 0, 'fev': 0, 'mar': 0, 'abr': 0,
                        'mai': 0, 'jun': 0, 'jul': 0, 'ago': 0,
                        'set': 0, 'out': 0, 'nov': 0, 'dez': 0
                    },
                    'approval_statuses': {}
                }
            
            # Somar percentuais por mês
            for mes in ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                       'jul', 'ago', 'set', 'out', 'nov', 'dez']:
                valor = str(d[mes]).replace('%', '').strip()
                if valor and valor != '0':
                    try:
                        subordinados[nome_colaborador]['monthly_allocations'][mes] += float(valor)
                    except:
                        pass
    
    return list(subordinados.values())