// Theme Management
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

// Theme toggle functionality
themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

function updateThemeIcon(theme) {
    const icon = themeToggle.querySelector('i');
    icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// Search and Filter Functionality
const searchInput = document.getElementById('search-input');
const clearSearchBtn = document.getElementById('clear-search');
const categoryFilter = document.getElementById('category-filter');
const commandsContainer = document.getElementById('commands-container');

let allCommands = [];
let filteredCommands = [];

// Load commands data
async function loadCommands() {
    try {
        const response = await fetch('data/commands.json');
        const data = await response.json();
        allCommands = data.categories.flatMap(category => 
            category.commands.map(cmd => ({...cmd, categoryName: category.name}))
        );
        filteredCommands = [...allCommands];
        renderCommands();
        updateStats();
    } catch (error) {
        console.error('Error loading commands:', error);
        commandsContainer.innerHTML = '<div class="loading">Error loading commands. Please refresh the page.</div>';
    }
}

// Render commands
function renderCommands() {
    if (filteredCommands.length === 0) {
        commandsContainer.innerHTML = '<div class="loading">No commands found matching your search.</div>';
        return;
    }

    commandsContainer.innerHTML = filteredCommands.map(command => `
        <div class="command-card" data-category="${command.category}">
            <div class="command-header">${command.name}</div>
            <div class="command-description">${command.description}</div>
            <div class="command-usage">${command.usage}</div>
            <div class="command-examples">
                <strong>Examples:</strong> ${command.examples.join(', ')}
            </div>
            <div class="command-permissions">
                <i class="fas fa-shield-alt"></i> ${command.permissions.join(', ')}
            </div>
            <button class="copy-btn" onclick="copyCommand('${command.usage}')">
                <i class="fas fa-copy"></i> Copy
            </button>
        </div>
    `).join('');
}

// Update statistics
function updateStats() {
    document.getElementById('total-commands').textContent = allCommands.length;
    document.getElementById('total-categories').textContent = new Set(allCommands.map(cmd => cmd.category)).size;
    document.getElementById('search-results').textContent = filteredCommands.length;
}

// Search functionality
searchInput.addEventListener('input', () => {
    const searchTerm = searchInput.value.toLowerCase();
    filterCommands(searchTerm, categoryFilter.value);
    
    // Show/hide clear button
    clearSearchBtn.classList.toggle('visible', searchTerm.length > 0);
});

// Clear search
clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    filterCommands('', categoryFilter.value);
    clearSearchBtn.classList.remove('visible');
});

// Category filter
categoryFilter.addEventListener('change', () => {
    filterCommands(searchInput.value.toLowerCase(), categoryFilter.value);
});

// Filter commands
function filterCommands(searchTerm, category) {
    filteredCommands = allCommands.filter(command => {
        const matchesSearch = !searchTerm || 
            command.name.toLowerCase().includes(searchTerm) ||
            command.description.toLowerCase().includes(searchTerm) ||
            command.usage.toLowerCase().includes(searchTerm) ||
            command.examples.some(ex => ex.toLowerCase().includes(searchTerm));
        
        const matchesCategory = category === 'all' || command.category === category;
        
        return matchesSearch && matchesCategory;
    });
    
    renderCommands();
    updateStats();
}

// Copy command to clipboard
async function copyCommand(command) {
    try {
        await navigator.clipboard.writeText(command);
        
        // Show feedback
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.backgroundColor = '#28a745';
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.backgroundColor = '';
        }, 2000);
    } catch (err) {
        console.error('Failed to copy: ', err);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
    }
    
    // Escape to clear search
    if (e.key === 'Escape' && searchInput.value) {
        searchInput.value = '';
        filterCommands('', categoryFilter.value);
        clearSearchBtn.classList.remove('visible');
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCommands();
    
    // Add keyboard shortcut hint
    const searchBar = document.querySelector('.search-bar');
    const hint = document.createElement('small');
    hint.textContent = 'Press Ctrl+K to search';
    hint.style.color = 'var(--text-secondary)';
    hint.style.fontSize = '0.8rem';
    hint.style.marginTop = '0.25rem';
    hint.style.display = 'block';
    searchBar.appendChild(hint);
});

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button
window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        if (!document.getElementById('scroll-to-top')) {
            const btn = document.createElement('button');
            btn.id = 'scroll-to-top';
            btn.innerHTML = '<i class="fas fa-chevron-up"></i>';
            btn.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: var(--accent-color);
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                cursor: pointer;
                box-shadow: 0 2px 10px var(--shadow-color);
                z-index: 1000;
                transition: all 0.3s;
            `;
            btn.addEventListener('click', scrollToTop);
            document.body.appendChild(btn);
        }
    } else {
        const btn = document.getElementById('scroll-to-top');
        if (btn) btn.remove();
    }
});
