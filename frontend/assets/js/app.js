
const API_BASE = '/api';

// Sidebar Injection
const sidebarHtml = `
    <div class="sidebar-logo">AIS OS</div>
    <a href="dashboard.html" class="nav-link">Dashboard</a>
    <a href="ai.html" class="nav-link">AI Employee</a>
    <a href="leads.html" class="nav-link">Leads</a>
    <a href="clients.html" class="nav-link">Clients</a>
    <a href="projects.html" class="nav-link">Projects</a>
    <a href="tasks.html" class="nav-link">Tasks</a>
    <a href="knowledge.html" class="nav-link">Knowledge Base</a>
    <a href="settings.html" class="nav-link">Settings</a>
`;

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.innerHTML = sidebarHtml;
        const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';
        const links = sidebar.querySelectorAll('.nav-link');
        links.forEach(link => {
            if (link.getAttribute('href') === currentPath) link.classList.add('active');
        });
    }
});

async function apiCall(endpoint, method = 'GET', body = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) options.body = JSON.stringify(body);
    try {
        const res = await fetch(API_BASE + endpoint, options);
        return await res.json();
    } catch (e) {
        console.error(e);
        alert('API Error: ' + e.message);
    }
}

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

async function loadModeIndicator() {
    const ind = document.getElementById('mode-indicator');
    if(!ind) return;
    try {
        const res = await apiCall('/ai/status');
        if(res.provider === 'gemini') {
            ind.innerHTML = '🟢 Gemini Live';
            ind.className = 'badge badge-active';
        } else {
            ind.innerHTML = '🟡 Demo Mode';
            ind.className = 'badge badge-new';
        }
    } catch(e) {
        ind.innerHTML = '🔴 Offline';
    }
}
document.addEventListener('DOMContentLoaded', loadModeIndicator);

async function loadDropdown(endpoint, selectId, labelField, valueField) {
    const select = document.getElementById(selectId);
    if (!select) return;
    try {
        const data = await apiCall(endpoint);
        let options = '<option value="">-- Select --</option>';
        data.forEach(item => {
            options += `<option value="${item[valueField]}">${item[labelField]}</option>`;
        });
        select.innerHTML = options;
    } catch(e) {
        console.error("Error loading dropdown", selectId, e);
    }
}
