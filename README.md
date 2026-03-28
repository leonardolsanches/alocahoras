# App de Alocação de Horas

Sistema empresarial para gerenciamento de alocação de horas de trabalho com autenticação, aprovação de gestores e integração com Power BI.

## 📁 Estrutura do Projeto

### Arquivos Principais
```
├── main.py                 # Ponto de entrada da aplicação
├── routes.py               # Rotas e lógica principal
├── models.py               # Modelos de dados de usuário
├── data_manager.py         # Gerenciamento de dados JSON
├── google_auth.py          # Autenticação Google OAuth
└── pyproject.toml          # Dependências do projeto
```

### Templates
```
templates/
├── base.html              # Template base
├── login.html             # Tela de login
├── calendario.html        # Calendário de alocação
└── aprovacao.html         # Tela de aprovação do gestor
```

### Assets Estáticos
```
static/
├── css/
│   └── style.css          # Estilos principais
└── js/
    ├── selection.js       # Funcionalidades de seleção
    ├── month-navigation.js # Navegação entre meses
    ├── approval-persistence.js # Persistência de aprovações
    └── color-persistence.js    # Persistência de cores
```

### Dados
```
data/                      # Dados JSON do sistema
├── users.json            # Usuários
├── collaborators.json    # Colaboradores
├── projects.json         # Projetos
├── activities.json       # Atividades
├── temas.json            # Temas/programas
└── allocations/          # Alocações por usuário
```

## 🗄️ Banco de Dados PostgreSQL

### Tabelas Principais
- `collaborators` - Colaboradores e hierarquia
- `projects` - Projetos autênticos
- `activities` - Atividades autênticas
- `allocation_types` - Tipos de alocação
- `allocations` - Alocações de horas
- `temas` - Temas com períodos de validade

## 🚀 Funcionalidades

### ✅ Implementado
- ✅ Login direto por nome
- ✅ Calendário de alocação mensal
- ✅ Aprovação/reprovação de alocações
- ✅ Navegação entre meses
- ✅ Persistência de aprovações
- ✅ Dados autênticos da planilha Excel
- ✅ Integração PostgreSQL para Power BI

### 🎯 Características
- Interface responsiva com tema dinâmico
- Dados autênticos (253 projetos, 27 atividades, 17 tipos)
- Hierarquia gestor-subordinado
- Cores de status (amarelo=pendente, verde=aprovado, vermelho=reprovado)
- Validação de períodos por tema

## 📊 Integração Power BI

O sistema está preparado para integração com Power BI através do PostgreSQL, fornecendo dados estruturados para análises empresariais.

## 🎨 Interface

- Logo Claro em todas as páginas
- Tema dinâmico baseado no horário
- Navegação intuitiva entre meses
- Seleção múltipla de células para aprovação
- Feedback visual das ações do usuário

---

**Desenvolvido para gestão eficiente de recursos e alocação de horas de trabalho.**