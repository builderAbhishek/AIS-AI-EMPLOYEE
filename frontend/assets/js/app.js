const API_BASE = '/api';

const sidebarHtml = `
    <div class="h-16 flex items-center px-6 border-b border-slate-200">
        <span class="text-primary font-bold text-xl tracking-tight">AIS OS</span>
    </div>
    <div class="flex-1 overflow-y-auto py-4 flex flex-col gap-1 px-3">
        <a href="dashboard.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors">Dashboard</a>
        <a href="ai.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors flex justify-between items-center">
            AI Employee <span class="bg-blue-100 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide">Live</span>
        </a>
        <div class="mt-4 mb-2 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">CRM</div>
        <a href="leads.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors">Leads</a>
        <a href="clients.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors">Clients</a>
        <a href="projects.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors">Projects</a>
        <a href="tasks.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors">Tasks</a>
        <div class="mt-4 mb-2 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">System</div>
        <a href="knowledge.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors">Knowledge Base</a>
        <a href="settings.html" class="nav-link px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-100 hover:text-primary transition-colors">Settings</a>
    </div>
`;

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.innerHTML = sidebarHtml;
        const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';
        const links = sidebar.querySelectorAll('.nav-link');
        links.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.remove('text-slate-600', 'hover:bg-slate-100');
                link.classList.add('bg-primary/10', 'text-primary', 'font-semibold');
            }
        });
    }
}

// Run immediately since script is at end of body
initSidebar();
loadModeIndicator();

async function apiCall(endpoint, method = 'GET', body = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) options.body = JSON.stringify(body);
    try {
        const res = await fetch(API_BASE + endpoint, options);
        if (!res.ok) {
            let msg = 'API Error';
            try { const err = await res.json(); msg = err.detail || msg; } catch(e){}
            throw new Error(msg);
        }
        return await res.json();
    } catch (e) {
        console.error(e);
        showToast(e.message, 'error');
        throw e;
    }
}

function openModal(id) { 
    const el = document.getElementById(id);
    if(el) {
        el.classList.remove('hidden');
        el.classList.add('flex');
    }
}

function closeModal(id) { 
    const el = document.getElementById(id);
    if(el) {
        el.classList.add('hidden');
        el.classList.remove('flex');
    }
}

async function loadModeIndicator() {
    const ind = document.getElementById('mode-indicator');
    if(!ind) return;
    try {
        const res = await apiCall('/ai/status');
        if(res.provider === 'ollama') {
            const thinkStr = res.thinking_mode === 'true' ? 'ON' : 'OFF';
            ind.innerHTML = `<div class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></div> 
                             <span class="font-bold text-green-700">Ollama Live</span> 
                             <span class="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded ml-1 text-slate-500">${res.model}</span>
                             <span class="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded ml-1 text-slate-500">Think: ${thinkStr}</span>`;
            ind.className = 'px-3 py-1.5 rounded-full text-xs font-semibold bg-green-50 border border-green-200 flex items-center gap-1.5';
        } else {
            ind.innerHTML = `<div class="w-2 h-2 rounded-full bg-red-500"></div> <span class="font-bold text-red-700">Ollama Offline</span>`;
            ind.className = 'px-3 py-1.5 rounded-full text-xs font-semibold bg-red-50 border border-red-200 flex items-center gap-1.5';
        }
    } catch(e) {
        ind.innerHTML = `<div class="w-2 h-2 rounded-full bg-red-500"></div> <span class="font-bold text-red-700">Ollama Offline</span>`;
        ind.className = 'px-3 py-1.5 rounded-full text-xs font-semibold bg-red-50 border border-red-200 flex items-center gap-1.5';
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if(!container) return;
    
    const toast = document.createElement('div');
    const isErr = type === 'error';
    toast.className = `px-4 py-3 rounded-lg shadow-lg text-sm font-medium text-white flex items-center gap-2 transform transition-all duration-300 translate-y-10 opacity-0 ${isErr ? 'bg-red-600' : 'bg-slate-800'}`;
    
    const icon = isErr ? 
        '<svg class="w-5 h-5 text-red-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>' : 
        '<svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>';
        
    toast.innerHTML = `${icon} ${message}`;
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-10', 'opacity-0');
    }, 10);
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function confirmAction(message, callback) {
    if(confirm(message)) {
        callback();
    }
}

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
