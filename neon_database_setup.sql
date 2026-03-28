-- Estrutura completa do banco PostgreSQL para Sistema de Alocação Claro
-- Execute este script no Neon após criar o banco

-- 1. Tabela principal com dados da planilha Excel
CREATE TABLE dados_planilha (
    id SERIAL PRIMARY KEY,
    colaboradores VARCHAR(255) NOT NULL,
    gestor_direto VARCHAR(255) NOT NULL,
    tipo_alocacao VARCHAR(255) NOT NULL,
    projetos VARCHAR(255) NOT NULL,
    atividades VARCHAR(255) NOT NULL,
    jan VARCHAR(10) DEFAULT '0',
    fev VARCHAR(10) DEFAULT '0',
    mar VARCHAR(10) DEFAULT '0',
    abr VARCHAR(10) DEFAULT '0',
    mai VARCHAR(10) DEFAULT '0',
    jun VARCHAR(10) DEFAULT '0',
    jul VARCHAR(10) DEFAULT '0',
    ago VARCHAR(10) DEFAULT '0',
    set VARCHAR(10) DEFAULT '0',
    out VARCHAR(10) DEFAULT '0',
    nov VARCHAR(10) DEFAULT '0',
    dez VARCHAR(10) DEFAULT '0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela para controle de aprovações
CREATE TABLE approval_status (
    id SERIAL PRIMARY KEY,
    manager_name VARCHAR(255) NOT NULL,
    collaborator_name VARCHAR(255) NOT NULL,
    month VARCHAR(10) NOT NULL,
    year VARCHAR(4) DEFAULT '2025',
    status VARCHAR(50) DEFAULT 'pendente',
    approved_by VARCHAR(255),
    approved_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Índices para melhor performance
CREATE INDEX idx_colaboradores ON dados_planilha(colaboradores);
CREATE INDEX idx_gestor_direto ON dados_planilha(gestor_direto);
CREATE INDEX idx_approval_manager ON approval_status(manager_name);
CREATE INDEX idx_approval_collaborator ON approval_status(collaborator_name);

-- 4. View para relatórios do Power BI
CREATE VIEW vw_allocations_powerbi AS
SELECT 
    dp.colaboradores as colaborador,
    dp.gestor_direto as gestor,
    dp.tipo_alocacao as tipo,
    dp.projetos as projeto,
    dp.atividades as atividade,
    CASE 
        WHEN dp.jan != '0' AND dp.jan IS NOT NULL THEN 'JAN'
        WHEN dp.fev != '0' AND dp.fev IS NOT NULL THEN 'FEV'
        WHEN dp.mar != '0' AND dp.mar IS NOT NULL THEN 'MAR'
        WHEN dp.abr != '0' AND dp.abr IS NOT NULL THEN 'ABR'
        WHEN dp.mai != '0' AND dp.mai IS NOT NULL THEN 'MAI'
        WHEN dp.jun != '0' AND dp.jun IS NOT NULL THEN 'JUN'
        WHEN dp.jul != '0' AND dp.jul IS NOT NULL THEN 'JUL'
        WHEN dp.ago != '0' AND dp.ago IS NOT NULL THEN 'AGO'
        WHEN dp.set != '0' AND dp.set IS NOT NULL THEN 'SET'
        WHEN dp.out != '0' AND dp.out IS NOT NULL THEN 'OUT'
        WHEN dp.nov != '0' AND dp.nov IS NOT NULL THEN 'NOV'
        WHEN dp.dez != '0' AND dp.dez IS NOT NULL THEN 'DEZ'
    END as mes,
    CASE 
        WHEN dp.jan != '0' AND dp.jan IS NOT NULL THEN CAST(REPLACE(dp.jan, '%', '') AS NUMERIC)
        WHEN dp.fev != '0' AND dp.fev IS NOT NULL THEN CAST(REPLACE(dp.fev, '%', '') AS NUMERIC)
        WHEN dp.mar != '0' AND dp.mar IS NOT NULL THEN CAST(REPLACE(dp.mar, '%', '') AS NUMERIC)
        WHEN dp.abr != '0' AND dp.abr IS NOT NULL THEN CAST(REPLACE(dp.abr, '%', '') AS NUMERIC)
        WHEN dp.mai != '0' AND dp.mai IS NOT NULL THEN CAST(REPLACE(dp.mai, '%', '') AS NUMERIC)
        WHEN dp.jun != '0' AND dp.jun IS NOT NULL THEN CAST(REPLACE(dp.jun, '%', '') AS NUMERIC)
        WHEN dp.jul != '0' AND dp.jul IS NOT NULL THEN CAST(REPLACE(dp.jul, '%', '') AS NUMERIC)
        WHEN dp.ago != '0' AND dp.ago IS NOT NULL THEN CAST(REPLACE(dp.ago, '%', '') AS NUMERIC)
        WHEN dp.set != '0' AND dp.set IS NOT NULL THEN CAST(REPLACE(dp.set, '%', '') AS NUMERIC)
        WHEN dp.out != '0' AND dp.out IS NOT NULL THEN CAST(REPLACE(dp.out, '%', '') AS NUMERIC)
        WHEN dp.nov != '0' AND dp.nov IS NOT NULL THEN CAST(REPLACE(dp.nov, '%', '') AS NUMERIC)
        WHEN dp.dez != '0' AND dp.dez IS NOT NULL THEN CAST(REPLACE(dp.dez, '%', '') AS NUMERIC)
    END as percentual,
    COALESCE(aps.status, 'pendente') as status_aprovacao
FROM dados_planilha dp
LEFT JOIN approval_status aps ON dp.colaboradores = aps.collaborator_name 
    AND dp.gestor_direto = aps.manager_name
WHERE CASE 
    WHEN dp.jan != '0' AND dp.jan IS NOT NULL THEN TRUE
    WHEN dp.fev != '0' AND dp.fev IS NOT NULL THEN TRUE
    WHEN dp.mar != '0' AND dp.mar IS NOT NULL THEN TRUE
    WHEN dp.abr != '0' AND dp.abr IS NOT NULL THEN TRUE
    WHEN dp.mai != '0' AND dp.mai IS NOT NULL THEN TRUE
    WHEN dp.jun != '0' AND dp.jun IS NOT NULL THEN TRUE
    WHEN dp.jul != '0' AND dp.jul IS NOT NULL THEN TRUE
    WHEN dp.ago != '0' AND dp.ago IS NOT NULL THEN TRUE
    WHEN dp.set != '0' AND dp.set IS NOT NULL THEN TRUE
    WHEN dp.out != '0' AND dp.out IS NOT NULL THEN TRUE
    WHEN dp.nov != '0' AND dp.nov IS NOT NULL THEN TRUE
    WHEN dp.dez != '0' AND dp.dez IS NOT NULL THEN TRUE
    ELSE FALSE
END;

-- 5. Função para inserir dados de aprovação
CREATE OR REPLACE FUNCTION insert_approval_status(
    p_manager_name VARCHAR(255),
    p_collaborator_name VARCHAR(255),
    p_month VARCHAR(10),
    p_status VARCHAR(50),
    p_approved_by VARCHAR(255) DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO approval_status (manager_name, collaborator_name, month, status, approved_by, approved_at)
    VALUES (p_manager_name, p_collaborator_name, p_month, p_status, p_approved_by, 
            CASE WHEN p_status = 'aprovado' THEN CURRENT_TIMESTAMP ELSE NULL END)
    ON CONFLICT (manager_name, collaborator_name, month) 
    DO UPDATE SET 
        status = EXCLUDED.status,
        approved_by = EXCLUDED.approved_by,
        approved_at = EXCLUDED.approved_at,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- 6. Trigger para atualizar timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_approval_timestamp
    BEFORE UPDATE ON approval_status
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- 7. Comentários nas tabelas
COMMENT ON TABLE dados_planilha IS 'Dados autênticos da planilha Excel com alocações mensais por colaborador';
COMMENT ON TABLE approval_status IS 'Controle de status de aprovação das alocações por gestor';
COMMENT ON VIEW vw_allocations_powerbi IS 'View otimizada para análises no Power BI';