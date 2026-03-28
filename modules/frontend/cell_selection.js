/**
 * Módulo de Seleção de Células - Solução Definitiva
 * Resolve: seleção de células, botão "Selecionar Todos", incrementos repetitivos
 */

class CellSelectionManager {
    constructor() {
        this.selectedCells = new Set();
        this.isProcessing = false;
        this.init();
    }

    init() {
        console.log('🔧 Inicializando gerenciador de seleção de células');
        this.setupEventListeners();
        this.setupButtons();
    }

    setupEventListeners() {
        // Event listener para clique em células
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('month-cell')) {
                this.handleCellClick(e.target);
            }
        });
    }

    setupButtons() {
        // Botão Selecionar Todas
        const selectAllBtn = document.getElementById('select-all-btn');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => this.selectAllCells());
        }

        // Botão Desmarcar Todas
        const deselectAllBtn = document.getElementById('deselect-all-btn');
        if (deselectAllBtn) {
            deselectAllBtn.addEventListener('click', () => this.deselectAllCells());
        }

        // Botão Aprovar Selecionadas
        const approveBtn = document.getElementById('approve-selected-btn');
        if (approveBtn) {
            approveBtn.addEventListener('click', () => this.approveSelected());
        }

        // Botão Reprovar Selecionadas
        const rejectBtn = document.getElementById('reject-selected-btn');
        if (rejectBtn) {
            rejectBtn.addEventListener('click', () => this.rejectSelected());
        }
    }

    handleCellClick(cell) {
        const text = cell.textContent.trim();
        if (!text || text === '-' || text === '0h') return;

        const cellId = this.generateCellId(cell);
        
        if (this.selectedCells.has(cellId)) {
            this.deselectCell(cell, cellId);
        } else {
            this.selectCell(cell, cellId);
        }
        
        this.updateDisplay();
    }

    selectCell(cell, cellId) {
        this.selectedCells.add(cellId);
        cell.classList.add('cell-selected');
        cell.style.border = '3px solid #007bff';
    }

    deselectCell(cell, cellId) {
        this.selectedCells.delete(cellId);
        cell.classList.remove('cell-selected');
        cell.style.border = '';
    }

    selectAllCells() {
        console.log('🎯 Selecionando todas as células válidas');
        
        const cells = document.querySelectorAll('.month-cell');
        this.selectedCells.clear();
        
        cells.forEach(cell => {
            const text = cell.textContent.trim();
            if (text && text !== '-' && text !== '0h') {
                const cellId = this.generateCellId(cell);
                this.selectCell(cell, cellId);
            }
        });
        
        this.updateDisplay();
    }

    deselectAllCells() {
        console.log('🧹 Desmarcando todas as células');
        
        this.selectedCells.forEach(cellId => {
            const cell = this.findCellById(cellId);
            if (cell) {
                this.deselectCell(cell, cellId);
            }
        });
        
        this.selectedCells.clear();
        this.updateDisplay();
    }

    approveSelected() {
        if (this.selectedCells.size === 0) {
            alert('Nenhuma célula selecionada');
            return;
        }

        if (this.isProcessing) {
            console.log('⚠️ Processamento em andamento, ignorando clique');
            return;
        }

        this.processApproval('aprovado', '#28a745');
    }

    rejectSelected() {
        if (this.selectedCells.size === 0) {
            alert('Nenhuma célula selecionada');
            return;
        }

        if (this.isProcessing) {
            console.log('⚠️ Processamento em andamento, ignorando clique');
            return;
        }

        this.processApproval('reprovado', '#dc3545');
    }

    processApproval(status, color) {
        this.isProcessing = true;
        console.log(`🎯 Processando ${status} para ${this.selectedCells.size} células`);
        
        // Atualização visual imediata
        this.selectedCells.forEach(cellId => {
            const cell = this.findCellById(cellId);
            if (cell) {
                cell.style.backgroundColor = color;
                cell.style.color = 'white';
                cell.classList.remove('cell-selected');
                cell.style.border = '';
            }
        });

        // Requisição para o servidor
        const data = {
            cells: Array.from(this.selectedCells),
            status: status
        };

        fetch('/api/approve_cells', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            console.log(`✅ ${status} processado com sucesso`);
        })
        .catch(error => {
            console.error(`❌ Erro no ${status}:`, error);
        })
        .finally(() => {
            this.selectedCells.clear();
            this.updateDisplay();
            this.isProcessing = false;
        });
    }

    generateCellId(cell) {
        const row = cell.parentNode.rowIndex || 0;
        const col = cell.cellIndex || 0;
        const text = cell.textContent.trim();
        return `cell-${row}-${col}-${text}`;
    }

    findCellById(cellId) {
        const cells = document.querySelectorAll('.month-cell');
        for (let cell of cells) {
            if (this.generateCellId(cell) === cellId) {
                return cell;
            }
        }
        return null;
    }

    updateDisplay() {
        const counter = document.getElementById('selection-count');
        const bulkActions = document.getElementById('bulk-actions');
        
        if (counter) {
            counter.textContent = `${this.selectedCells.size} células selecionadas`;
        }
        
        if (bulkActions) {
            bulkActions.style.display = this.selectedCells.size > 0 ? 'block' : 'none';
        }
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando módulo de seleção de células');
    window.cellManager = new CellSelectionManager();
});

console.log('✅ Módulo CellSelection carregado');