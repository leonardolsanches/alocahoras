"""
Módulo de Carregamento de Dados Autênticos
Garante que todos os dados do Excel estejam corretamente carregados no PostgreSQL
"""

import pandas as pd
import psycopg2
import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class AuthenticDataLoader:
    def __init__(self):
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Estabelece conexão com PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=os.environ['PGHOST'],
                database=os.environ['PGDATABASE'],
                user=os.environ['PGUSER'],
                password=os.environ['PGPASSWORD'],
                port=os.environ['PGPORT']
            )
            self.connection.autocommit = True
            logger.info("✅ Conexão PostgreSQL estabelecida para carregamento")
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            raise
    
    def verify_authentic_data_completeness(self) -> Dict[str, int]:
        """Verifica se todos os dados autênticos estão carregados"""
        cursor = self.connection.cursor()
        
        stats = {}
        
        # Verificar colaboradores
        cursor.execute("SELECT COUNT(DISTINCT full_name) FROM collaborators")
        stats['total_collaborators'] = cursor.fetchone()[0]
        
        # Verificar alocações
        cursor.execute("SELECT COUNT(*) FROM allocations")
        stats['total_allocations'] = cursor.fetchone()[0]
        
        # Verificar projetos únicos
        cursor.execute("SELECT COUNT(DISTINCT project_name) FROM allocations")
        stats['unique_projects'] = cursor.fetchone()[0]
        
        # Verificar atividades únicas
        cursor.execute("SELECT COUNT(DISTINCT activity_name) FROM allocations")
        stats['unique_activities'] = cursor.fetchone()[0]
        
        # Verificar tipos de alocação
        cursor.execute("SELECT COUNT(DISTINCT allocation_type) FROM allocations")
        stats['allocation_types'] = cursor.fetchone()[0]
        
        # Verificar gestor Aline
        cursor.execute("SELECT COUNT(*) FROM collaborators WHERE full_name = 'ALINE JULIANA LOPES'")
        stats['aline_exists'] = cursor.fetchone()[0]
        
        # Verificar subordinados da Aline
        cursor.execute("SELECT COUNT(*) FROM collaborators WHERE manager_id = '1'")
        stats['aline_subordinates'] = cursor.fetchone()[0]
        
        cursor.close()
        
        logger.info(f"📊 Verificação de dados autênticos: {stats}")
        return stats
    
    def load_excel_data_if_missing(self, excel_path: str = "attached_assets/dados.xlsx") -> bool:
        """Carrega dados do Excel se estiverem em falta"""
        try:
            # Verificar se arquivo existe
            if not os.path.exists(excel_path):
                logger.warning(f"❌ Arquivo Excel não encontrado: {excel_path}")
                return False
            
            # Ler dados da aba ALOCACAO
            df = pd.read_excel(excel_path, sheet_name='ALOCACAO')
            logger.info(f"📋 Excel carregado: {len(df)} registros encontrados")
            
            # Verificar se dados já estão carregados
            stats = self.verify_authentic_data_completeness()
            if stats['total_allocations'] >= len(df):
                logger.info("✅ Dados já estão carregados corretamente")
                return True
            
            # Carregar dados se necessário
            return self._process_excel_data(df)
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar Excel: {e}")
            return False
    
    def _process_excel_data(self, df: pd.DataFrame) -> bool:
        """Processa e carrega dados do Excel no PostgreSQL"""
        cursor = self.connection.cursor()
        
        try:
            # Limpar tabelas existentes
            cursor.execute("TRUNCATE TABLE allocations CASCADE")
            cursor.execute("TRUNCATE TABLE collaborators CASCADE")
            
            # Processar colaboradores únicos
            collaborators = {}
            collaborator_id = 1
            
            for _, row in df.iterrows():
                collaborator_name = str(row['COLABORADOR']).strip()
                manager_name = str(row['GESTOR DIRETO']).strip()
                
                if collaborator_name not in collaborators:
                    collaborators[collaborator_name] = {
                        'id': str(collaborator_id),
                        'name': collaborator_name,
                        'manager_name': manager_name
                    }
                    collaborator_id += 1
            
            # Inserir colaboradores
            for collab_data in collaborators.values():
                # Encontrar ID do gestor
                manager_id = None
                for other_collab in collaborators.values():
                    if other_collab['name'] == collab_data['manager_name']:
                        manager_id = other_collab['id']
                        break
                
                cursor.execute("""
                    INSERT INTO collaborators (id, full_name, manager_id, user_type)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    collab_data['id'],
                    collab_data['name'],
                    manager_id,
                    'headcount'
                ))
            
            # Inserir alocações
            allocation_id = 1
            for _, row in df.iterrows():
                collaborator_name = str(row['COLABORADOR']).strip()
                collaborator_id = collaborators[collaborator_name]['id']
                
                # Processar cada mês
                months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 
                         'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
                
                for month_idx, month in enumerate(months, 1):
                    if month in row and pd.notna(row[month]) and row[month] != 0:
                        cursor.execute("""
                            INSERT INTO allocations (
                                id, collaborator_id, allocation_type, project_name, 
                                activity_name, hours, percentage, status, 
                                start_date, end_date
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            str(allocation_id),
                            collaborator_id,
                            str(row['TIPO ALOCACAO']).strip(),
                            str(row['PROJETOS']).strip(),
                            str(row['ATIVIDADES']).strip(),
                            float(row[month]) if pd.notna(row[month]) else 0,
                            float(row[month]) / 168 * 100 if pd.notna(row[month]) else 0,  # Conversão para percentual
                            'pendente',
                            f'2025-{month_idx:02d}-01',
                            f'2025-{month_idx:02d}-28'
                        ))
                        allocation_id += 1
            
            cursor.close()
            
            # Verificar carregamento
            final_stats = self.verify_authentic_data_completeness()
            logger.info(f"✅ Dados carregados com sucesso: {final_stats}")
            
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"❌ Erro ao processar dados: {e}")
            return False
    
    def ensure_aline_login_available(self) -> bool:
        """Garante que Aline está disponível para login"""
        cursor = self.connection.cursor()
        
        try:
            # Verificar se Aline existe
            cursor.execute("SELECT id FROM collaborators WHERE full_name = 'ALINE JULIANA LOPES'")
            result = cursor.fetchone()
            
            if not result:
                # Inserir Aline se não existir
                cursor.execute("""
                    INSERT INTO collaborators (id, full_name, manager_id, user_type)
                    VALUES ('1', 'ALINE JULIANA LOPES', NULL, 'manager')
                    ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name
                """)
                logger.info("✅ Aline inserida/atualizada no banco")
            
            cursor.close()
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"❌ Erro ao garantir login da Aline: {e}")
            return False
    
    def close_connection(self):
        """Fecha conexão"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Conexão de carregamento fechada")

# Função utilitária para uso direto
def ensure_authentic_data_loaded():
    """Garante que dados autênticos estão carregados"""
    loader = AuthenticDataLoader()
    
    try:
        # Verificar e carregar dados se necessário
        stats = loader.verify_authentic_data_completeness()
        
        if stats['total_allocations'] < 100:  # Se tem menos de 100 alocações, recarregar
            logger.info("🔄 Carregando dados autênticos do Excel...")
            loader.load_excel_data_if_missing()
        
        # Garantir que Aline está disponível
        loader.ensure_aline_login_available()
        
        # Verificação final
        final_stats = loader.verify_authentic_data_completeness()
        logger.info(f"🎯 Dados autênticos prontos: {final_stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao garantir dados: {e}")
        return False
    
    finally:
        loader.close_connection()