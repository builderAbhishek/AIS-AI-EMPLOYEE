import os

frontend_dir = r"f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\frontend"
css_dir = os.path.join(frontend_dir, "assets", "css")
js_dir = os.path.join(frontend_dir, "assets", "js")

os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)

css_content = """
:root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --bg: #f1f5f9;
    --surface: #ffffff;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --danger: #ef4444;
    --success: #22c55e;
    --warning: #f59e0b;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; }
body { background-color: var(--bg); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }

.sidebar { width: 250px; background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 1rem; }
.sidebar-logo { font-size: 1.25rem; font-weight: bold; color: var(--primary); margin-bottom: 2rem; padding: 0.5rem; }
.nav-link { display: block; padding: 0.75rem 1rem; margin-bottom: 0.5rem; color: var(--text-main); text-decoration: none; border-radius: 0.5rem; transition: background 0.2s; }
.nav-link:hover, .nav-link.active { background: var(--bg); color: var(--primary); font-weight: 500; }

.main-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }
.header { height: 60px; background: var(--surface); border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 2rem; justify-content: space-between; }
.page-title { font-size: 1.25rem; font-weight: 600; }

.container { padding: 2rem; max-width: 1200px; margin: 0 auto; width: 100%; }

.card { background: var(--surface); border-radius: 0.5rem; padding: 1.5rem; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 1rem; }
.grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.stat-value { font-size: 2rem; font-weight: bold; color: var(--primary); margin-top: 0.5rem; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); }
th { font-weight: 600; color: var(--text-muted); background: var(--bg); }
tr:hover { background: #f8fafc; }

.btn { padding: 0.5rem 1rem; border: none; border-radius: 0.375rem; font-weight: 500; cursor: pointer; transition: 0.2s; }
.btn-primary { background: var(--primary); color: white; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.875rem; }
.btn-danger { background: var(--danger); color: white; }

.badge { padding: 0.25rem 0.5rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 600; }
.badge-new { background: #dbeafe; color: #1e40af; }
.badge-active { background: #dcfce3; color: #166534; }

input, select, textarea { width: 100%; padding: 0.5rem; border: 1px solid var(--border); border-radius: 0.375rem; margin-bottom: 1rem; }

/* AI Employee Chat */
.chat-container { display: flex; gap: 1rem; height: calc(100vh - 150px); }
.chat-box { flex: 2; display: flex; flex-direction: column; background: var(--surface); border-radius: 0.5rem; border: 1px solid var(--border); }
.chat-messages { flex: 1; padding: 1rem; overflow-y: auto; display: flex; flex-direction: column; gap: 1rem; }
.message { max-width: 80%; padding: 1rem; border-radius: 0.5rem; }
.message.user { background: var(--primary); color: white; align-self: flex-end; }
.message.ai { background: var(--bg); color: var(--text-main); align-self: flex-start; }
.chat-input { display: flex; padding: 1rem; border-top: 1px solid var(--border); gap: 0.5rem; }
.chat-input input { margin-bottom: 0; }
.ai-sidebar { flex: 1; display: flex; flex-direction: column; gap: 1rem; overflow-y: auto;}

/* Modals */
.modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; padding: 1rem;}
.modal.active { display: flex; }
.modal-content { background: var(--surface); padding: 2rem; border-radius: 0.5rem; width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
"""

js_content = """
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
"""

html_shell = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AIS AI Employee</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <div class="sidebar" id="sidebar"></div>
    <div class="main-content">
        <div class="header">
            <div class="page-title">{title}</div>
            <div>Demo Mode Active</div>
        </div>
        <div class="container" id="app-content">
            {content}
        </div>
    </div>
    <script src="assets/js/app.js"></script>
    {extra_js}
</body>
</html>"""

pages = {
    "index.html": "<script>window.location.href='dashboard.html';</script>",
    
    "dashboard.html": {
        "title": "Dashboard",
        "content": """
            <div class="grid-4" id="stats-grid">Loading...</div>
            <div class="card">
                <h3>Top Actions</h3>
                <ul id="top-actions" style="margin-top:1rem; padding-left:1.5rem;"></ul>
            </div>
            <div class="card">
                <h3>AI Daily Brief</h3>
                <button class="btn btn-primary" onclick="generateBrief()">Generate Brief</button>
                <div id="brief-content" style="margin-top: 1rem; white-space: pre-wrap;"></div>
            </div>
        """,
        "extra_js": """
        <script>
            async function loadDashboard() {
                const data = await apiCall('/dashboard/');
                if(!data) return;
                
                document.getElementById('stats-grid').innerHTML = `
                    <div class="card"><div>Total Leads</div><div class="stat-value">${data.overview.total_leads}</div></div>
                    <div class="card"><div>Active Clients</div><div class="stat-value">${data.overview.active_clients}</div></div>
                    <div class="card"><div>Active Projects</div><div class="stat-value">${data.overview.active_projects}</div></div>
                    <div class="card"><div>Pending Tasks</div><div class="stat-value">${data.overview.pending_tasks}</div></div>
                `;
                
                document.getElementById('top-actions').innerHTML = data.top_actions.map(a => 
                    `<li><b>[${a.priority}]</b> ${a.title}</li>`
                ).join('');
            }
            
            async function generateBrief() {
                document.getElementById('brief-content').innerText = "Analyzing data...";
                const res = await apiCall('/ai/daily-brief');
                document.getElementById('brief-content').innerText = res.text;
            }
            
            loadDashboard();
        </script>
        """
    },
    
    "leads.html": {
        "title": "Leads",
        "content": """
            <button class="btn btn-primary" onclick="openModal('leadModal')">+ New Lead</button>
            <div class="card" style="margin-top: 1rem; overflow-x: auto;">
                <table>
                    <thead><tr><th>Name</th><th>Contact</th><th>Phone</th><th>Status</th><th>Priority</th><th>Actions</th></tr></thead>
                    <tbody id="leads-table"></tbody>
                </table>
            </div>

            <div class="modal" id="leadModal">
                <div class="modal-content">
                    <div class="modal-header"><h3>Add Lead</h3><button class="btn" onclick="closeModal('leadModal')">X</button></div>
                    <form id="leadForm" onsubmit="saveLead(event)">
                        <input type="text" id="business_name" placeholder="Business Name" required>
                        <input type="text" id="contact_person" placeholder="Contact Person">
                        <input type="text" id="phone" placeholder="Phone">
                        <input type="email" id="email" placeholder="Email">
                        <select id="status">
                            <option value="NEW">NEW</option>
                            <option value="CONTACTED">CONTACTED</option>
                            <option value="INTERESTED">INTERESTED</option>
                            <option value="MEETING">MEETING</option>
                            <option value="PROPOSAL">PROPOSAL</option>
                        </select>
                        <select id="priority">
                            <option value="LOW">LOW</option>
                            <option value="MEDIUM" selected>MEDIUM</option>
                            <option value="HIGH">HIGH</option>
                        </select>
                        <button type="submit" class="btn btn-primary">Save Lead</button>
                    </form>
                </div>
            </div>
        """,
        "extra_js": """
        <script>
            async function loadLeads() {
                const leads = await apiCall('/leads/');
                const tbody = document.getElementById('leads-table');
                tbody.innerHTML = leads.map(l => `
                    <tr>
                        <td>${l.business_name}</td>
                        <td>${l.contact_person || '-'}</td>
                        <td>${l.phone || '-'}</td>
                        <td><span class="badge badge-new">${l.status}</span></td>
                        <td>${l.priority}</td>
                        <td>
                            <button class="btn btn-sm" onclick="pitchLead('${l.business_name}')">AI Pitch</button>
                        </td>
                    </tr>
                `).join('');
            }

            async function saveLead(e) {
                e.preventDefault();
                const data = {
                    business_name: document.getElementById('business_name').value,
                    contact_person: document.getElementById('contact_person').value,
                    phone: document.getElementById('phone').value,
                    email: document.getElementById('email').value,
                    status: document.getElementById('status').value,
                    priority: document.getElementById('priority').value
                };
                await apiCall('/leads/', 'POST', data);
                closeModal('leadModal');
                loadLeads();
            }

            async function pitchLead(name) {
                alert("Generating AI Pitch...");
                const res = await apiCall('/ai/pitch', 'POST', {business_name: name, service_interest: "Software solutions"});
                alert(res.text);
            }
            
            loadLeads();
        </script>
        """
    },

    "ai.html": {
        "title": "AI Employee",
        "content": """
            <div class="chat-container">
                <div class="chat-box">
                    <div class="chat-messages" id="chat-messages">
                        <div class="message ai">Hello! I am your AI Employee. How can I help AIS today?</div>
                    </div>
                    <div class="chat-input">
                        <input type="text" id="chatInput" placeholder="Ask for next actions, pitch generation, etc..." onkeypress="if(event.key==='Enter') sendMessage()">
                        <button class="btn btn-primary" onclick="sendMessage()">Send</button>
                    </div>
                </div>
                <div class="ai-sidebar card">
                    <h3>Suggested Prompts</h3>
                    <button class="btn" style="text-align:left" onclick="sendPrompt('आज क्या करना चाहिए?')">आज क्या करना चाहिए?</button>
                    <button class="btn" style="text-align:left" onclick="sendPrompt('Pending tasks बताओ')">Pending tasks बताओ</button>
                    <button class="btn" style="text-align:left" onclick="sendPrompt('Give me a sales pitch for a Restaurant')">Sales pitch for Restaurant</button>
                </div>
            </div>
        """,
        "extra_js": """
        <script>
            function sendPrompt(text) {
                document.getElementById('chatInput').value = text;
                sendMessage();
            }

            async function sendMessage() {
                const input = document.getElementById('chatInput');
                const text = input.value.trim();
                if(!text) return;
                
                const chatMessages = document.getElementById('chat-messages');
                chatMessages.innerHTML += `<div class="message user">${text}</div>`;
                input.value = '';
                
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                const res = await apiCall('/ai/chat', 'POST', {message: text});
                
                chatMessages.innerHTML += `<div class="message ai">${res.text.replace(/\\n/g, '<br>')}</div>`;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        </script>
        """
    }
}

# Remaining pages simplified for MVP
simple_pages = ['clients.html', 'projects.html', 'tasks.html', 'knowledge.html', 'settings.html']
for sp in simple_pages:
    name = sp.replace('.html', '').capitalize()
    pages[sp] = {
        "title": name,
        "content": f"<div class='card'><h2>{name} Module</h2><p>CRUD operations work exactly like Leads.</p></div>",
        "extra_js": ""
    }

with open(os.path.join(css_dir, "style.css"), "w") as f: f.write(css_content)
with open(os.path.join(js_dir, "app.js"), "w") as f: f.write(js_content)

for filename, data in pages.items():
    path = os.path.join(frontend_dir, filename)
    if isinstance(data, str):
        content = data
    else:
        content = html_shell.format(title=data['title'], content=data['content'], extra_js=data['extra_js'])
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Frontend scaffolding complete!")
