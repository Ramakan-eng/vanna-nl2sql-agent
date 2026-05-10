/**
 * Healthcare NL2SQL - Enhanced Frontend JavaScript
 * Features: Typing indicator, auto-complete, toast notifications, sortable table, charts
 */

// ============================================
// Configuration
// ============================================
const API_BASE_URL = 'http://localhost:8000';
const MAX_HISTORY_ITEMS = 50;

// ============================================
// State Management
// ============================================
let state = {
    history: [],
    currentResult: null,
    currentPage: 1,
    totalPages: 1,
    itemsPerPage: 20,
    isDarkMode: false,
    sortColumn: null,
    sortDirection: 'asc',
    filteredRows: [],
    autocompleteIndex: -1
};

// ============================================
// DOM Elements
// ============================================
const elements = {
    // Chat
    questionInput: document.getElementById('questionInput'),
    sendBtn: document.getElementById('sendBtn'),
    chatContainer: document.getElementById('chatContainer'),
    autocompleteDropdown: document.getElementById('autocompleteDropdown'),

    // Results
    resultsPanel: document.getElementById('resultsPanel'),
    sqlQuery: document.getElementById('sqlQuery'),
    tableHead: document.getElementById('tableHead'),
    tableBody: document.getElementById('tableBody'),
    chartContainer: document.getElementById('chartContainer'),
    chart: document.getElementById('chart'),
    exportCsvBtn: document.getElementById('exportCsvBtn'),
    closeResults: document.getElementById('closeResults'),
    rowCount: document.getElementById('rowCount'),

    // Table controls
    tableSearch: document.getElementById('tableSearch'),
    pageSize: document.getElementById('pageSize'),

    // Pagination
    firstPage: document.getElementById('firstPage'),
    prevPage: document.getElementById('prevPage'),
    nextPage: document.getElementById('nextPage'),
    lastPage: document.getElementById('lastPage'),
    pageInfo: document.getElementById('pageInfo'),
    pagination: document.getElementById('pagination'),

    // History
    historyList: document.getElementById('historyList'),
    clearHistory: document.getElementById('clearHistory'),

    // Suggestions
    suggestionList: document.getElementById('suggestionList'),

    // Theme
    toggleTheme: document.getElementById('toggleTheme'),
    themeIcon: document.getElementById('themeIcon'),

    // Loading
    loadingOverlay: document.getElementById('loadingOverlay'),

    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// ============================================
// Suggestions for auto-complete
// ============================================
const SUGGESTIONS = [
    "How many patients do we have?",
    "List all patients from Delhi",
    "List all male patients",
    "Which city has the most patients?",
    "How many doctors are there?",
    "Which doctor has the most appointments?",
    "Show appointments per doctor",
    "Show all completed appointments",
    "Show cancelled appointments",
    "Show appointments for January 2026",
    "Show appointments by doctor",
    "What is the total revenue?",
    "Show unpaid invoices",
    "What is the average invoice amount?",
    "Show revenue by doctor",
    "Show appointments in the last 3 months",
    "Show monthly appointment trend",
    "Show all patients",
    "Show doctors by department",
    "Total treatments cost"
];

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    loadTheme();
    setupEventListeners();
    setupExampleButtons();
    setupSuggestionChips();
    setupChartControls();
});

function setupEventListeners() {
    // Send question
    elements.sendBtn.addEventListener('click', sendQuestion);
    elements.questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            if (elements.autocompleteDropdown.classList.contains('active')) {
                selectAutocompleteItem();
            } else {
                sendQuestion();
            }
        }
    });

    // Autocomplete navigation
    elements.questionInput.addEventListener('input', handleAutocomplete);
    elements.questionInput.addEventListener('keydown', handleAutocompleteKeydown);
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.input-wrapper')) {
            hideAutocomplete();
        }
    });

    // Export CSV
    elements.exportCsvBtn.addEventListener('click', exportToCsv);

    // Close results
    elements.closeResults.addEventListener('click', () => {
        elements.resultsPanel.style.display = 'none';
    });

    // Pagination
    elements.firstPage.addEventListener('click', () => goToPage(1));
    elements.prevPage.addEventListener('click', () => goToPage(state.currentPage - 1));
    elements.nextPage.addEventListener('click', () => goToPage(state.currentPage + 1));
    elements.lastPage.addEventListener('click', () => goToPage(state.totalPages));

    // Table controls
    elements.tableSearch.addEventListener('input', handleTableSearch);
    elements.pageSize.addEventListener('change', (e) => {
        state.itemsPerPage = parseInt(e.target.value);
        state.currentPage = 1;
        renderTable();
    });

    // History
    elements.clearHistory.addEventListener('click', clearHistory);

    // Theme
    elements.toggleTheme.addEventListener('click', toggleTheme);
}

function setupExampleButtons() {
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.dataset.question;
            elements.questionInput.value = question;
            sendQuestion();
        });
    });
}

function setupSuggestionChips() {
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            elements.questionInput.value = chip.textContent;
            elements.questionInput.focus();
        });
    });
}

function setupChartControls() {
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            // Chart type change would require re-rendering - simplified for now
        });
    });
}

// ============================================
// Auto-complete
// ============================================
function handleAutocomplete() {
    const input = elements.questionInput.value.toLowerCase().trim();

    if (input.length < 2) {
        hideAutocomplete();
        return;
    }

    const matches = SUGGESTIONS.filter(s => s.toLowerCase().includes(input));

    if (matches.length === 0) {
        hideAutocomplete();
        return;
    }

    showAutocomplete(matches.slice(0, 5));
}

function showAutocomplete(items) {
    state.autocompleteIndex = -1;
    elements.autocompleteDropdown.innerHTML = items.map((item, index) => `
        <div class="autocomplete-item" data-index="${index}" data-value="${escapeHtml(item)}">
            <i class="fas fa-search"></i>
            <span>${escapeHtml(item)}</span>
        </div>
    `).join('');

    elements.autocompleteDropdown.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
            elements.questionInput.value = item.dataset.value;
            hideAutocomplete();
            sendQuestion();
        });
    });

    elements.autocompleteDropdown.classList.add('active');
}

function hideAutocomplete() {
    elements.autocompleteDropdown.classList.remove('active');
    state.autocompleteIndex = -1;
}

function handleAutocompleteKeydown(e) {
    const items = elements.autocompleteDropdown.querySelectorAll('.autocomplete-item');

    if (!elements.autocompleteDropdown.classList.contains('active') || items.length === 0) {
        return;
    }

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        state.autocompleteIndex = Math.min(state.autocompleteIndex + 1, items.length - 1);
        updateAutocompleteSelection(items);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        state.autocompleteIndex = Math.max(state.autocompleteIndex - 1, 0);
        updateAutocompleteSelection(items);
    }
}

function updateAutocompleteSelection(items) {
    items.forEach((item, index) => {
        item.classList.toggle('selected', index === state.autocompleteIndex);
    });
}

function selectAutocompleteItem() {
    const items = elements.autocompleteDropdown.querySelectorAll('.autocomplete-item');
    if (state.autocompleteIndex >= 0 && state.autocompleteIndex < items.length) {
        elements.questionInput.value = items[state.autocompleteIndex].dataset.value;
        hideAutocomplete();
    }
}

// ============================================
// API Calls
// ============================================
async function sendQuestion() {
    const question = elements.questionInput.value.trim();

    if (!question) {
        return;
    }

    // Disable input
    elements.questionInput.disabled = true;
    elements.sendBtn.disabled = true;

    // Add user message
    addMessageToChat('user', question);
    elements.questionInput.value = '';

    // Show typing indicator
    showLoading(true);

    // Create history entry
    const historyEntry = {
        id: generateId(),
        question: question,
        timestamp: new Date().toISOString(),
        status: 'pending'
    };

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        const result = await response.json();

        historyEntry.status = response.ok ? 'success' : 'error';
        historyEntry.sqlQuery = result.sql_query;
        historyEntry.rowCount = result.row_count;

        // Add assistant response
        addMessageToChat('assistant', result.message, result);

        state.currentResult = result;
        state.currentPage = 1;
        state.filteredRows = [];

        if (response.ok && result.sql_query) {
            displayResults(result);
            elements.resultsPanel.style.display = 'block';
            showToast('Query executed successfully', 'success');
        }

    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('assistant', 'Sorry, an error occurred while processing your request.');
        historyEntry.status = 'error';
        historyEntry.error = error.message;
        showToast('Error processing request', 'error');
    } finally {
        elements.questionInput.disabled = false;
        elements.sendBtn.disabled = false;
        elements.questionInput.focus();
        showLoading(false);
        addToHistory(historyEntry);
    }
}

// ============================================
// Chat Display
// ============================================
function addMessageToChat(role, content, result = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role === 'user' ? 'user-message' : 'assistant-message'}`;

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    if (role === 'user') {
        messageContent.innerHTML = `<p>${escapeHtml(content)}</p>`;
    } else {
        let html = `<p>${escapeHtml(content)}</p>`;

        if (result) {
            if (result.sql_query) {
                html += `<div class="sql-code">${escapeHtml(result.sql_query)}</div>`;
            }
            if (result.row_count !== null) {
                html += `<p style="margin-top: 10px; font-size: 0.8rem; color: var(--text-muted);">
                    <i class="fas fa-database"></i> ${result.row_count} row${result.row_count !== 1 ? 's' : ''} returned
                </p>`;
            }
        }

        messageContent.innerHTML = html;
    }

    messageDiv.appendChild(messageContent);
    elements.chatContainer.appendChild(messageDiv);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

// ============================================
// Results Display
// ============================================
function displayResults(result) {
    elements.sqlQuery.querySelector('code').textContent = result.sql_query || 'No query generated';
    elements.rowCount.textContent = `${result.row_count || 0} rows`;

    state.filteredRows = [];
    state.sortColumn = null;
    state.sortDirection = 'asc';

    state.totalPages = result.rows && result.rows.length > 0
        ? Math.ceil(result.rows.length / state.itemsPerPage)
        : 1;

    renderTable(result.columns, result.rows);

    if (result.rows && result.rows.length > state.itemsPerPage) {
        elements.pagination.style.display = 'flex';
    } else {
        elements.pagination.style.display = 'none';
    }

    if (result.chart) {
        elements.chartContainer.style.display = 'block';
        Plotly.newPlot('chart', result.chart.data, result.chart.layout, { responsive: true });
    } else {
        elements.chartContainer.style.display = 'none';
    }
}

function renderTable(columns, rows) {
    elements.tableHead.innerHTML = '';
    elements.tableBody.innerHTML = '';

    if (!columns || !rows || columns.length === 0) {
        return;
    }

    // Filter rows if search is active
    let displayRows = state.filteredRows.length > 0 ? state.filteredRows : rows;

    // Sort if needed
    if (state.sortColumn !== null) {
        displayRows = sortRows(displayRows, columns);
    }

    // Render headers
    const headerRow = document.createElement('tr');
    columns.forEach((col, index) => {
        const th = document.createElement('th');
        th.innerHTML = `
            ${escapeHtml(col)}
            <span class="sort-icon">
                ${state.sortColumn === index
                    ? (state.sortDirection === 'asc' ? '<i class="fas fa-sort-up"></i>' : '<i class="fas fa-sort-down"></i>')
                    : '<i class="fas fa-sort"></i>'}
            </span>
        `;
        th.addEventListener('click', () => toggleSort(index));
        if (state.sortColumn === index) {
            th.classList.add('sorted');
        }
        headerRow.appendChild(th);
    });
    elements.tableHead.appendChild(headerRow);

    // Calculate page slice
    const startIndex = (state.currentPage - 1) * state.itemsPerPage;
    const endIndex = Math.min(startIndex + state.itemsPerPage, displayRows.length);
    const pageRows = displayRows.slice(startIndex, endIndex);

    // Render body
    pageRows.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell !== null ? cell : 'NULL';
            tr.appendChild(td);
        });
        elements.tableBody.appendChild(tr);
    });

    // Update pagination
    elements.pageInfo.textContent = `Page ${state.currentPage} of ${Math.max(1, Math.ceil(displayRows.length / state.itemsPerPage))}`;
    elements.firstPage.disabled = state.currentPage === 1;
    elements.prevPage.disabled = state.currentPage === 1;
    elements.nextPage.disabled = state.currentPage >= Math.ceil(displayRows.length / state.itemsPerPage);
    elements.lastPage.disabled = state.currentPage >= Math.ceil(displayRows.length / state.itemsPerPage);
}

function toggleSort(columnIndex) {
    if (state.sortColumn === columnIndex) {
        state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        state.sortColumn = columnIndex;
        state.sortDirection = 'asc';
    }
    state.currentPage = 1;
    renderTable();
}

function sortRows(rows, columns) {
    if (state.sortColumn === null) return rows;

    return [...rows].sort((a, b) => {
        let valA = a[state.sortColumn];
        let valB = b[state.sortColumn];

        // Handle nulls
        if (valA === null) return 1;
        if (valB === null) return -1;

        // Numeric comparison
        if (typeof valA === 'number' && typeof valB === 'number') {
            return state.sortDirection === 'asc' ? valA - valB : valB - valA;
        }

        // String comparison
        valA = String(valA).toLowerCase();
        valB = String(valB).toLowerCase();

        if (state.sortDirection === 'asc') {
            return valA.localeCompare(valB);
        } else {
            return valB.localeCompare(valA);
        }
    });
}

function handleTableSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();

    if (!searchTerm || !state.currentResult || !state.currentResult.rows) {
        state.filteredRows = [];
    } else {
        const { columns, rows } = state.currentResult;
        state.filteredRows = rows.filter(row =>
            row.some(cell => String(cell).toLowerCase().includes(searchTerm))
        );
    }

    state.currentPage = 1;
    state.totalPages = state.filteredRows.length > 0
        ? Math.ceil(state.filteredRows.length / state.itemsPerPage)
        : (state.currentResult?.rows ? Math.ceil(state.currentResult.rows.length / state.itemsPerPage) : 1);

    renderTable();
}

function goToPage(page) {
    if (page < 1) page = 1;

    const totalRows = state.filteredRows.length || state.currentResult?.rows?.length || 0;
    const maxPage = Math.ceil(totalRows / state.itemsPerPage);

    if (page > maxPage) page = maxPage;
    if (page < 1) page = 1;

    state.currentPage = page;
    renderTable();
}

// ============================================
// CSV Export
// ============================================
function exportToCsv() {
    if (!state.currentResult || !state.currentResult.rows) {
        showToast('No data to export', 'error');
        return;
    }

    const { columns, rows } = state.currentResult;
    const csvRows = [columns.join(',')];

    rows.forEach(row => {
        const escapedRow = row.map(cell => {
            if (cell === null) return '';
            const str = String(cell);
            if (str.includes(',') || str.includes('"') || str.includes('\n')) {
                return `"${str.replace(/"/g, '""')}"`;
            }
            return str;
        });
        csvRows.push(escapedRow.join(','));
    });

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `query_results_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('CSV exported successfully', 'success');
}

// ============================================
// History Management
// ============================================
function addToHistory(entry) {
    // Remove duplicate
    state.history = state.history.filter(h => h.question !== entry.question);
    state.history.unshift(entry);

    if (state.history.length > MAX_HISTORY_ITEMS) {
        state.history = state.history.slice(0, MAX_HISTORY_ITEMS);
    }

    saveHistory();
    renderHistory();
}

function renderHistory() {
    elements.historyList.innerHTML = '';

    if (state.history.length === 0) {
        elements.historyList.innerHTML = `
            <p style="text-align: center; color: var(--text-muted); padding: 20px; font-size: 0.85rem;">
                No queries yet
            </p>
        `;
        return;
    }

    state.history.forEach(entry => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="question">${escapeHtml(entry.question)}</div>
            <div class="meta">
                <span class="status ${entry.status}">
                    <i class="fas fa-${entry.status === 'success' ? 'check' : 'times'}"></i>
                    ${entry.status}
                </span>
                <span>${formatDate(entry.timestamp)}</span>
            </div>
        `;

        item.addEventListener('click', () => {
            elements.questionInput.value = entry.question;
            elements.questionInput.focus();
        });

        elements.historyList.appendChild(item);
    });
}

function clearHistory() {
    if (confirm('Clear all history?')) {
        state.history = [];
        saveHistory();
        renderHistory();
        showToast('History cleared', 'info');
    }
}

function saveHistory() {
    try {
        localStorage.setItem('nl2sql_history', JSON.stringify(state.history));
    } catch (e) {
        console.warn('Could not save history');
    }
}

function loadHistory() {
    try {
        const saved = localStorage.getItem('nl2sql_history');
        if (saved) {
            state.history = JSON.parse(saved);
            renderHistory();
        }
    } catch (e) {
        console.warn('Could not load history');
    }
}

// ============================================
// Theme Management
// ============================================
function toggleTheme() {
    state.isDarkMode = !state.isDarkMode;

    if (state.isDarkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        elements.themeIcon.className = 'fas fa-sun';
    } else {
        document.documentElement.removeAttribute('data-theme');
        elements.themeIcon.className = 'fas fa-moon';
    }

    saveTheme();
}

function saveTheme() {
    try {
        localStorage.setItem('nl2sql_theme', state.isDarkMode ? 'dark' : 'light');
    } catch (e) {
        console.warn('Could not save theme');
    }
}

function loadTheme() {
    try {
        const saved = localStorage.getItem('nl2sql_theme');
        if (saved === 'dark') {
            state.isDarkMode = true;
            document.documentElement.setAttribute('data-theme', 'dark');
            elements.themeIcon.className = 'fas fa-sun';
        }
    } catch (e) {
        console.warn('Could not load theme');
    }
}

// ============================================
// Toast Notifications
// ============================================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        info: 'fa-info-circle'
    };

    toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// Loading
// ============================================
function showLoading(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

// ============================================
// Utilities
// ============================================
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

    return date.toLocaleDateString();
}