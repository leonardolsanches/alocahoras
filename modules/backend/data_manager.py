"""
Módulo de Gerenciamento de Dados - Backend
Garante carregamento correto e consistente dos dados autênticos
"""

import psycopg2
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Conecta ao PostgreSQL com dados autênticos"""
        try:
            self.connection = psycopg2.connect(
                host=os.environ['PGHOST'],
                database=os.environ['PGDATABASE'],
                user=os.environ['PGUSER'],
                password=os.environ['PGPASSWORD'],
                port=os.environ['PGPORT']
            )
            logger.info("✅ Conexão PostgreSQL estabelecida")
        except Exception as e:
            logger.error(f"❌ Erro na conexão PostgreSQL: {e}")
            raise
    
    def get_authentic_collaborators(self) -> List[Dict[str, Any]]:
        """Retorna colaboradores autênticos do banco"""
        cursor = self.connection.cursor()
        
        query = """
        SELECT DISTINCT c.id, c.full_name, c.manager_id, c.user_type
        FROM collaborators c
        ORDER BY c.full_name
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        collaborators = []
        for row in results:
            collaborators.append({
                'id': row[0],
                'name': row[1],
                'manager_id': row[2],
                'user_type': row[3]
            })
        
        cursor.close()
        logger.info(f"✅ {len(collaborators)} colaboradores autênticos carregados")
        return collaborators
    
    def get_manager_subordinates(self, manager_id: str) -> List[Dict[str, Any]]:
        """Retorna subordinados diretos de um gestor"""
        cursor = self.connection.cursor()
        
        query = """
        SELECT DISTINCT c.id, c.full_name, COUNT(a.id) as total_allocations,
               COUNT(CASE WHEN a.status = 'pendente' THEN 1 END) as pending_count
        FROM collaborators c
        LEFT JOIN allocations a ON c.id = a.collaborator_id
        WHERE c.manager_id = %s
        GROUP BY c.id, c.full_name
        ORDER BY c.full_name
        """
        
        cursor.execute(query, (manager_id,))
        results = cursor.fetchall()
        
        subordinates = []
        for row in results:
            subordinates.append({
                'id': row[0],
                'name': row[1],
                'total_allocations': row[2],
                'pending_count': row[3]
            })
        
        cursor.close()
        logger.info(f"✅ {len(subordinates)} subordinados carregados para gestor {manager_id}")
        return subordinates
    
    def get_allocation_data(self, collaborator_id: str, month: int, year: int) -> List[Dict[str, Any]]:
        """Retorna alocações autênticas de um colaborador para um mês específico"""
        cursor = self.connection.cursor()
        
        query = """
        SELECT a.id, a.allocation_type, a.project_name, a.activity_name, 
               a.hours, a.percentage, a.status, a.start_date, a.end_date
        FROM allocations a
        WHERE a.collaborator_id = %s
        AND EXTRACT(MONTH FROM a.start_date) <= %s
        AND EXTRACT(MONTH FROM a.end_date) >= %s
        AND EXTRACT(YEAR FROM a.start_date) = %s
        ORDER BY a.allocation_type, a.project_name
        """
        
        cursor.execute(query, (collaborator_id, month, month, year))
        results = cursor.fetchall()
        
        allocations = []
        for row in results:
            allocations.append({
                'id': row[0],
                'allocation_type': row[1],
                'project_name': row[2],
                'activity_name': row[3],
                'hours': row[4],
                'percentage': row[5],
                'status': row[6],
                'start_date': row[7],
                'end_date': row[8]
            })
        
        cursor.close()
        return allocations
    
    def update_allocation_status(self, allocation_ids: List[str], status: str) -> bool:
        """Atualiza status de alocações sem duplicação"""
        cursor = self.connection.cursor()
        
        try:
            # Usar transação para garantir atomicidade
            self.connection.autocommit = False
            
            query = """
            UPDATE allocations 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = ANY(%s)
            """
            
            cursor.execute(query, (status, allocation_ids))
            affected_rows = cursor.rowcount
            
            self.connection.commit()
            self.connection.autocommit = True
            
            cursor.close()
            logger.info(f"✅ {affected_rows} alocações atualizadas para status '{status}'")
            return True
            
        except Exception as e:
            self.connection.rollback()
            self.connection.autocommit = True
            cursor.close()
            logger.error(f"❌ Erro ao atualizar status: {e}")
            return False
    
    def get_projects_and_activities(self) -> Dict[str, List[str]]:
        """Retorna projetos e atividades autênticos"""
        cursor = self.connection.cursor()
        
        # Buscar projetos únicos
        cursor.execute("SELECT DISTINCT project_name FROM allocations ORDER BY project_name")
        projects = [row[0] for row in cursor.fetchall()]
        
        # Buscar atividades únicas
        cursor.execute("SELECT DISTINCT activity_name FROM allocations ORDER BY activity_name")
        activities = [row[0] for row in cursor.fetchall()]
        
        # Buscar tipos de alocação únicos
        cursor.execute("SELECT DISTINCT allocation_type FROM allocations ORDER BY allocation_type")
        allocation_types = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        
        return {
            'projects': projects,
            'activities': activities,
            'allocation_types': allocation_types
        }
    
    def verify_data_integrity(self) -> Dict[str, int]:
        """Verifica integridade dos dados autênticos"""
        cursor = self.connection.cursor()
        
        stats = {}
        
        # Contar colaboradores
        cursor.execute("SELECT COUNT(*) FROM collaborators")
        stats['collaborators'] = cursor.fetchone()[0]
        
        # Contar alocações
        cursor.execute("SELECT COUNT(*) FROM allocations")
        stats['allocations'] = cursor.fetchone()[0]
        
        # Contar alocações pendentes
        cursor.execute("SELECT COUNT(*) FROM allocations WHERE status = 'pendente'")
        stats['pending_allocations'] = cursor.fetchone()[0]
        
        # Contar projetos únicos
        cursor.execute("SELECT COUNT(DISTINCT project_name) FROM allocations")
        stats['unique_projects'] = cursor.fetchone()[0]
        
        cursor.close()
        
        logger.info(f"📊 Integridade dos dados verificada: {stats}")
        return stats
    
    def close_connection(self):
        """Fecha conexão com o banco"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Conexão PostgreSQL fechada")

# Instância global para uso na aplicação
data_manager = DataManager()