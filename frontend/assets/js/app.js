
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
