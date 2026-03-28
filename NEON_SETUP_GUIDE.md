# Guia de Configuração do Banco PostgreSQL no Neon

## 1. Criar Banco no Neon

1. Acesse [console.neon.tech](https://console.neon.tech)
2. Clique em "Create Project"
3. Escolha nome do projeto: `sistema-alocacao-claro`
4. Região: `us-west-2` (ou mais próxima)
5. PostgreSQL version: `16` (mais recente)

## 2. Obter Credenciais

Após criar o projeto, copie a string de conexão:
```
postgresql://username:password@host/database?sslmode=require
```

Exemplo:
```
postgresql://neondb_owner:abc123xyz@ep-example-123.us-west-2.aws.neon.tech/neondb?sslmode=require
```

## 3. Executar Scripts de Configuração

### Passo 1: Criar Estrutura
Execute o conteúdo do arquivo `neon_database_setup.sql` no console SQL do Neon:

1. No painel do Neon, vá em "SQL Editor"
2. Cole todo o conteúdo de `neon_database_setup.sql`
3. Clique em "Run Query"

### Passo 2: Carregar Dados
1. Configure a variável de ambiente no Replit:
   ```bash
   DATABASE_URL = sua_string_de_conexao_completa
   ```

2. Execute o script de carregamento:
   ```bash
   python load_excel_data.py
   ```

## 4. Verificar Instalação

Execute estas queries no SQL Editor do Neon para verificar:

```sql
-- Verificar tabelas criadas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Contar registros
SELECT COUNT(*) as total_registros FROM dados_planilha;

-- Verificar colaboradores únicos
SELECT COUNT(DISTINCT colaboradores) as colaboradores_unicos FROM dados_planilha;

-- Testar alguns usuários específicos
SELECT colaboradores, gestor_direto, jan, fev, mar 
FROM dados_planilha 
WHERE colaboradores IN ('ANDRE LUIS LINS RAMOS', 'ADRIANO GARROTE TORRESAN')
LIMIT 5;
```

## 5. Configurar no Replit

Adicione estas variáveis de ambiente no Replit:

```bash
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
PGHOST=host_do_neon
PGPORT=5432
PGDATABASE=neondb
PGUSER=username
PGPASSWORD=password
```

## 6. Estrutura Final

Após a configuração, o banco terá:

### Tabelas:
- `dados_planilha`: 828 registros autênticos da planilha Excel
- `approval_status`: Controle de aprovações por gestor

### View:
- `vw_allocations_powerbi`: Dados otimizados para Power BI

### Índices:
- Performance otimizada para consultas por colaborador e gestor

## 7. Testagem

O sistema deve carregar:
- ✅ 828 registros de alocação
- ✅ 284 colaboradores únicos  
- ✅ 54 gestores únicos
- ✅ 253 projetos únicos
- ✅ Alocações mensais autênticas (jan-dez)

## 8. Solução de Problemas

### Erro de Conexão:
- Verificar se endpoint está ativo no Neon
- Confirmar string de conexão completa
- Testar conectividade com `psql`

### Dados Não Carregam:
- Verificar se arquivo Excel existe em `attached_assets/`
- Confirmar estrutura da planilha (aba 'ALOCACAO')
- Verificar permissões de escrita no banco

### Performance:
- Índices são criados automaticamente
- View otimizada para Power BI
- Considerar connection pooling para produção

## 9. Backup e Manutenção

```sql
-- Backup dos dados
COPY dados_planilha TO '/tmp/backup_dados.csv' DELIMITER ',' CSV HEADER;

-- Limpar dados antigos (se necessário)
DELETE FROM approval_status WHERE updated_at < NOW() - INTERVAL '30 days';
```

## 10. Conectar Power BI

Use a string de conexão PostgreSQL no Power BI:
- Servidor: `host_do_neon`
- Banco: `neondb`  
- Usuário: `username`
- Senha: `password`
- Usar query: `SELECT * FROM vw_allocations_powerbi`