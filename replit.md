# Sistema de Alocação de Horas - Claro

## Overview

Sistema empresarial para gerenciamento de alocação de horas de trabalho com autenticação, aprovação de gestores e integração com Power BI. O sistema permite que gestores visualizem e aprovem as alocações de seus subordinados em uma interface de calendário anual, com dados autênticos carregados diretamente do PostgreSQL.

**Status Atual**: Sistema totalmente funcional com banco PostgreSQL Neon ativo e 828 registros autênticos da planilha Excel carregados.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Flask web application with Jinja2 templates
- **UI Components**: Bootstrap 5 for responsive design, custom CSS for calendar views
- **JavaScript**: Vanilla JS for interactive features (cell selection, month navigation, approval workflows)
- **Templates**: Base template with specialized views for login, calendar, and approval screens

### Backend Architecture
- **Web Framework**: Flask with Flask-Login for session management
- **Authentication**: Simple password-based login with user selection dropdown
- **Data Layer**: PostgreSQL database as the single source of truth
- **API Structure**: RESTful endpoints for dashboard data, approval actions, and user management

### Data Storage Solutions
- **Primary Database**: PostgreSQL hosted on Neon (cloud PostgreSQL service)
- **Schema Design**: 
  - `collaborators` - Employee hierarchy and management structure
  - `allocations` - Time allocation records with monthly breakdown
  - `projects` - Project definitions and metadata
  - `activities` - Activity types and categories
  - `allocation_types` - Classification of work types
  - `approval_status` - Approval workflow state management

## Key Components

### 1. Data Management
- **PostgreSQL Migration**: Complete migration from JSON files to PostgreSQL for data authenticity
- **Excel Integration**: Direct loading of authentic data from Excel spreadsheets into database
- **Fallback System**: Excel-based fallback when PostgreSQL is unavailable

### 2. User Interface Components
- **Calendar View**: Annual calendar showing monthly allocations with color-coded status
- **Approval Interface**: Hierarchical drill-down (Type → Project → Activity) for detailed approvals
- **Dashboard**: Monthly view with analytics and subordinate management
- **Navigation**: Month-by-month navigation with persistent selections

### 3. Approval Workflow
- **Cell Selection**: Interactive calendar cells for bulk selection and approval
- **Status Management**: Pending (yellow), Approved (green), Rejected (red) states
- **Persistence**: Approval states saved to PostgreSQL for consistency across sessions

## Data Flow

1. **Data Input**: Excel spreadsheet with authentic company data (828 allocation records)
2. **Database Loading**: Python scripts load Excel data into PostgreSQL tables
3. **Web Interface**: Flask routes serve data from PostgreSQL to HTML templates
4. **User Interaction**: Managers select and approve allocations through calendar interface
5. **State Persistence**: Approval decisions saved back to PostgreSQL
6. **Reporting**: Power BI connects directly to PostgreSQL for real-time reporting

## External Dependencies

### Database Infrastructure
- **Neon PostgreSQL**: Cloud-hosted PostgreSQL database (July 2025 - Active)
- **Connection**: Environment variable `DATABASE_URL` for database connection string
- **Database URL**: `postgresql://neondb_owner:npg_v5buj1ETdLIP@ep-still-tree-ac1q7wl0-pooler.sa-east-1.aws.neon.tech/neondb`
- **Data Status**: 828 registros autênticos carregados da planilha Excel, 283 colaboradores únicos

### Python Libraries
- **Flask**: Web framework and routing
- **Flask-Login**: User session management
- **psycopg2**: PostgreSQL database adapter
- **pandas**: Excel file processing and data manipulation
- **openpyxl**: Excel file reading capabilities

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements

## Deployment Strategy

### Environment Setup
1. **Database**: Create PostgreSQL database on Neon platform ✅ **CONCLUÍDO**
2. **Schema**: Execute `neon_database_setup.sql` to create table structure ✅ **CONCLUÍDO**
3. **Data Loading**: Run `load_excel_data.py` to populate with authentic data ✅ **CONCLUÍDO**
4. **Environment Variables**: Configure `DATABASE_URL` for database connection ✅ **CONCLUÍDO**

### Recent Changes (July 2025)
- **Database Migration**: Migrou do banco Neon anterior (endpoint desabilitado) para novo banco ativo
- **Data Loading**: Carregou 828 registros autênticos da planilha Excel usando `quick_load_data.py`
- **Connection Fix**: DATABASE_URL hardcoded em `app.py` e `routes.py` para garantir conexão estável
- **Verification**: Sistema totalmente funcional com dados reais carregados

### File Structure
- **Entry Point**: `main.py` imports and runs Flask application
- **Configuration**: `app.py` sets up Flask app with session management
- **Routes**: `routes.py` handles all web endpoints and authentication
- **Models**: `models.py` defines user authentication classes
- **Data Scripts**: Various Python scripts for database management and Excel loading

### Archived Components
- **JSON Legacy**: Previous JSON-based data storage moved to `archived_files/`
- **Migration Scripts**: Database migration and synchronization utilities
- **Template Iterations**: Previous UI implementations preserved for reference

The system prioritizes data authenticity by using PostgreSQL as the single source of truth, with direct Excel integration for initial data loading and Power BI connectivity for reporting.