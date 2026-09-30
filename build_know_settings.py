import os
from build_ui import write_file, base_layout

# --- KNOWLEDGE BASE ---
knowledge_html = """
<div class="mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
    <div class="relative w-full md:w-96">
        <svg class="w-5 h-5 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="searchInput" placeholder="Search knowledge base..." class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" oninput="loadKnowledge()">
    </div>
    <button onclick="openModal('addKnowledgeModal')" class="w-full md:w-auto bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primaryHover transition-colors flex items-center justify-center gap-2 shadow-sm">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        New Document
    </button>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="knowledge-grid">
    <div class="col-span-full text-center text-slate-500 py-8">Loading knowledge base...</div>
</div>
"""

knowledge_modals = """
<!-- Add Knowledge Modal -->
<div id="addKnowledgeModal" class="modal fixed inset-0 bg-slate-900/50 z-50 justify-center items-center p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-slate-800">Add Knowledge Document</h3>
            <button onclick="closeModal('addKnowledgeModal')" class="text-slate-400 hover:text-slate-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="p-6 overflow-y-auto">
            <form id="addKnowledgeForm" onsubmit="addKnowledge(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Title</label>
                    <input type="text" id="title" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Category</label>
                    <input type="text" id="category" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Content</label>
                    <textarea id="content" rows="6" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono text-sm"></textarea>
                </div>
                <div class="pt-4 border-t border-slate-200 flex justify-end gap-3">
                    <button type="button" onclick="closeModal('addKnowledgeModal')" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primaryHover transition-colors shadow-sm">Save Document</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""

knowledge_scripts = """
<script>
    async function loadKnowledge() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        try {
            const data = await apiCall('/knowledge/');
            const grid = document.getElementById('knowledge-grid');
            grid.innerHTML = '';
            
            const filtered = data.filter(k => k.title.toLowerCase().includes(query) || (k.category && k.category.toLowerCase().includes(query)));
            
            if (filtered.length === 0) {
                grid.innerHTML = '<div class="col-span-full text-center text-slate-500 py-8 bg-white border border-slate-200 rounded-xl border-dashed">No documents found.</div>';
                return;
            }

            filtered.forEach(k => {
                grid.innerHTML += `
                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col h-64">
                        <div class="px-5 py-4 border-b border-slate-100 flex justify-between items-start gap-2">
                            <div>
                                <h3 class="font-semibold text-slate-800 line-clamp-1" title="${k.title}">${k.title}</h3>
                                <span class="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full mt-1 inline-block">${k.category || 'General'}</span>
                            </div>
                            <button onclick="deleteKnowledge(${k.id})" class="text-slate-400 hover:text-red-600 shrink-0" title="Delete">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                            </button>
                        </div>
                        <div class="p-5 flex-1 overflow-y-auto text-sm text-slate-600 font-mono whitespace-pre-wrap text-xs">
                            ${k.content}
                        </div>
                    </div>
                `;
            });
        } catch (e) {
            console.error(e);
        }
    }

    async function addKnowledge(e) {
        e.preventDefault();
        const payload = {
            title: document.getElementById('title').value,
            category: document.getElementById('category').value,
            content: document.getElementById('content').value
        };
        await apiCall('/knowledge/', 'POST', payload);
        closeModal('addKnowledgeModal');
        document.getElementById('addKnowledgeForm').reset();
        showToast('Document saved');
        loadKnowledge();
    }

    async function deleteKnowledge(id) {
        confirmAction("Delete this document?", async () => {
            await apiCall(`/knowledge/${id}`, 'DELETE');
            showToast('Document deleted');
            loadKnowledge();
        });
    }

    document.addEventListener('DOMContentLoaded', loadKnowledge);
</script>
"""

write_file("knowledge.html", base_layout.format(
    title="Knowledge Base", page_title="Knowledge Base", header_extra="", 
    content=knowledge_html, scripts=knowledge_scripts, modals=knowledge_modals
))


# --- SETTINGS ---
settings_html = """
<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
    <!-- Connection Status -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200 bg-slate-50">
            <h3 class="font-semibold text-slate-800">Connection Status</h3>
        </div>
        <div class="p-6 space-y-4 text-sm text-slate-700">
            <div class="flex justify-between py-2 border-b border-slate-100">
                <span class="font-medium">Provider</span>
                <span id="status-provider" class="font-bold">OLLAMA</span>
            </div>
            <div class="flex justify-between py-2 border-b border-slate-100">
                <span class="font-medium">Status</span>
                <span id="status-connection" class="font-bold text-slate-400">Checking...</span>
            </div>
            <div class="flex justify-between py-2 border-b border-slate-100">
                <span class="font-medium">Model</span>
                <span id="status-model" class="font-mono text-xs bg-slate-100 px-2 py-0.5 rounded">...</span>
            </div>
            <div class="flex justify-between py-2">
                <span class="font-medium">Last Test</span>
                <span id="status-time" class="text-slate-500">Never</span>
            </div>
        </div>
    </div>

    <!-- AI Configuration -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200 bg-slate-50">
            <h3 class="font-semibold text-slate-800">AI Configuration</h3>
        </div>
        <div class="p-6">
            <form id="settingsForm" onsubmit="saveSettings(event)" class="space-y-5">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">AI Provider</label>
                    <select id="AI_PROVIDER" class="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-slate-500 cursor-not-allowed" disabled>
                        <option value="ollama">Ollama (Local)</option>
                    </select>
                    <p class="text-xs text-slate-500 mt-1">AIS operates strictly with local models for privacy. Cloud fallback is disabled.</p>
                </div>

                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Ollama Base URL</label>
                    <input type="text" id="OLLAMA_BASE_URL" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono text-sm" placeholder="http://127.0.0.1:11434">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Ollama Model</label>
                    <div class="flex gap-2">
                        <select id="OLLAMA_MODEL" class="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono text-sm">
                            <option value="">Loading models...</option>
                        </select>
                        <button type="button" class="px-3 py-2 bg-slate-100 text-slate-600 hover:bg-slate-200 rounded-lg font-medium transition-colors" onclick="fetchOllamaModels()">
                            Refresh
                        </button>
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Thinking Mode</label>
                    <select id="OLLAMA_THINKING_MODE" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-medium">
                        <option value="false">OFF</option>
                        <option value="true">ON</option>
                    </select>
                    <p class="text-xs text-slate-500 mt-1">Enables or disables explicit "think" mode for local models.</p>
                </div>

                <div class="pt-4 border-t border-slate-200 flex flex-col sm:flex-row gap-3">
                    <button type="submit" class="flex-1 bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primaryHover transition-colors shadow-sm text-center">Save Settings</button>
                    <button type="button" onclick="testConnection()" class="flex-1 bg-white border border-slate-300 text-slate-700 px-4 py-2 rounded-lg font-medium hover:bg-slate-50 transition-colors shadow-sm text-center">Test Connection</button>
                </div>
            </form>
            
            <div id="test-alert" class="mt-4 hidden p-4 rounded-lg text-sm font-medium border"></div>
        </div>
    </div>
</div>
"""

settings_scripts = """
<script>
    let loadedOllamaModel = "";
    
    async function fetchOllamaModels() {
        const select = document.getElementById('OLLAMA_MODEL');
        select.innerHTML = '<option value="">Fetching...</option>';
        try {
            const models = await apiCall('/ai/models');
            if (models.error) {
                select.innerHTML = '<option value="">Ollama Offline</option>';
                return;
            }
            select.innerHTML = '';
            if(models.length === 0) {
                select.innerHTML = '<option value="">No models found</option>';
            } else {
                models.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.name;
                    opt.innerText = m.name;
                    select.appendChild(opt);
                });
                if (loadedOllamaModel) {
                    select.value = loadedOllamaModel;
                }
            }
        } catch(e) {
            select.innerHTML = '<option value="">Error loading</option>';
        }
    }

    async function loadSettings() {
        const settings = await apiCall('/settings/');
        if(!settings) return;
        
        document.getElementById('OLLAMA_BASE_URL').value = settings.OLLAMA_BASE_URL || 'http://127.0.0.1:11434';
        document.getElementById('OLLAMA_THINKING_MODE').value = settings.OLLAMA_THINKING_MODE || 'false';
        loadedOllamaModel = settings.OLLAMA_MODEL || '';
        
        document.getElementById('status-provider').innerText = 'OLLAMA';
        document.getElementById('status-model').innerText = settings.OLLAMA_MODEL || '-';
        
        fetchOllamaModels();
        checkHealth();
    }
    
    async function checkHealth() {
        try {
            const health = await apiCall('/ai/health');
            const conn = document.getElementById('status-connection');
            if (health.status === 'connected') {
                conn.innerText = 'Connected';
                conn.className = 'font-bold text-green-600';
            } else {
                conn.innerText = 'Offline';
                conn.className = 'font-bold text-red-600';
            }
        } catch(e) {
            const conn = document.getElementById('status-connection');
            conn.innerText = 'Offline';
            conn.className = 'font-bold text-red-600';
        }
    }

    async function saveSettings(e) {
        e.preventDefault();
        
        const payload = {
            settings: [
                {key: 'AI_PROVIDER', value: 'ollama'},
                {key: 'OLLAMA_BASE_URL', value: document.getElementById('OLLAMA_BASE_URL').value},
                {key: 'OLLAMA_MODEL', value: document.getElementById('OLLAMA_MODEL').value},
                {key: 'OLLAMA_THINKING_MODE', value: document.getElementById('OLLAMA_THINKING_MODE').value}
            ]
        };

        await apiCall('/settings/', 'POST', payload);
        showToast('Settings saved securely');
        loadSettings();
    }

    async function testConnection() {
        const alertBox = document.getElementById('test-alert');
        alertBox.classList.remove('hidden');
        alertBox.className = 'mt-4 p-4 rounded-lg text-sm font-medium border bg-slate-50 text-slate-700 border-slate-200 flex items-center gap-2';
        alertBox.innerHTML = '<svg class="animate-spin h-4 w-4 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Testing connection (Timeout: 300s)...';
        
        try {
            const res = await apiCall('/ai/test-connection', 'POST');
            if(res.success) {
                alertBox.className = 'mt-4 p-4 rounded-lg text-sm font-medium border bg-green-50 text-green-700 border-green-200';
                alertBox.innerText = 'Connected successfully. ' + (res.message || '');
            } else {
                alertBox.className = 'mt-4 p-4 rounded-lg text-sm font-medium border bg-red-50 text-red-700 border-red-200';
                alertBox.innerText = res.message;
            }
        } catch (e) {
            alertBox.className = 'mt-4 p-4 rounded-lg text-sm font-medium border bg-red-50 text-red-700 border-red-200';
            alertBox.innerText = 'Connection test failed: ' + e.message;
        }
        
        document.getElementById('status-time').innerText = new Date().toLocaleString();
        checkHealth();
    }

    document.addEventListener('DOMContentLoaded', loadSettings);
</script>
"""

write_file("settings.html", base_layout.format(
    title="Settings", page_title="System Settings", header_extra="", 
    content=settings_html, scripts=settings_scripts, modals=""
))

print("Knowledge and Settings rebuilt.")
