import os
from build_ui import write_file, base_layout

html_content = """
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8" id="stats-grid">
    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-pulse"><div class="h-4 bg-slate-200 rounded w-1/2 mb-4"></div><div class="h-8 bg-slate-200 rounded w-1/4"></div></div>
    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-pulse"><div class="h-4 bg-slate-200 rounded w-1/2 mb-4"></div><div class="h-8 bg-slate-200 rounded w-1/4"></div></div>
    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-pulse"><div class="h-4 bg-slate-200 rounded w-1/2 mb-4"></div><div class="h-8 bg-slate-200 rounded w-1/4"></div></div>
    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-pulse"><div class="h-4 bg-slate-200 rounded w-1/2 mb-4"></div><div class="h-8 bg-slate-200 rounded w-1/4"></div></div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Top Priorities -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col">
        <div class="px-6 py-4 border-b border-slate-100 font-semibold text-slate-800 flex justify-between items-center">
            Top Priority Tasks
            <a href="tasks.html" class="text-primary text-sm font-medium hover:underline">View All</a>
        </div>
        <div class="p-6 flex-1">
            <ul id="top-actions" class="space-y-3">
                <li class="text-slate-500 text-sm italic">Loading tasks...</li>
            </ul>
        </div>
    </div>

    <!-- AI Daily Brief -->
    <div class="lg:col-span-2 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl border border-indigo-100 shadow-sm flex flex-col">
        <div class="px-6 py-4 border-b border-indigo-100 flex justify-between items-center">
            <h3 class="font-semibold text-indigo-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                AI Daily Brief
            </h3>
            <button onclick="generateBrief()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-1.5 rounded-md text-sm font-medium shadow-sm transition-colors flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                Regenerate Brief
            </button>
        </div>
        <div class="p-6 flex-1 prose prose-indigo max-w-none text-slate-700 text-sm">
            <div id="brief-content" class="whitespace-pre-wrap leading-relaxed">Click "Regenerate Brief" to analyze today's business data and get your AI action plan.</div>
        </div>
    </div>
</div>
"""

scripts = """
<script>
    async function loadDashboard() {
        const data = await apiCall('/dashboard/');
        if(!data) return;
        
        document.getElementById('stats-grid').innerHTML = `
            <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <div class="text-slate-500 text-sm font-medium mb-1">Active Projects</div>
                <div class="text-3xl font-bold text-slate-800">${data.overview.active_projects}</div>
            </div>
            <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <div class="text-slate-500 text-sm font-medium mb-1">Active Clients</div>
                <div class="text-3xl font-bold text-slate-800">${data.overview.active_clients}</div>
            </div>
            <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <div class="text-slate-500 text-sm font-medium mb-1">Pending Tasks</div>
                <div class="text-3xl font-bold text-slate-800">${data.overview.pending_tasks}</div>
            </div>
            <div class="bg-white p-6 rounded-xl border border-red-200 shadow-sm hover:shadow-md transition-shadow">
                <div class="text-red-500 text-sm font-medium mb-1">Overdue Tasks</div>
                <div class="text-3xl font-bold text-red-600">${data.overview.overdue_tasks}</div>
            </div>
        `;
        
        const topActionsEl = document.getElementById('top-actions');
        if (data.top_actions && data.top_actions.length > 0) {
            topActionsEl.innerHTML = data.top_actions.map(a => {
                const color = a.priority === 'HIGH' ? 'text-red-600 bg-red-50 ring-red-500/20' : 
                            (a.priority === 'MEDIUM' ? 'text-amber-600 bg-amber-50 ring-amber-500/20' : 'text-green-600 bg-green-50 ring-green-500/20');
                return `
                <li class="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
                    <span class="mt-0.5 inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${color}">${a.priority}</span>
                    <span class="text-sm text-slate-700 font-medium">${a.title}</span>
                </li>`;
            }).join('');
        } else {
            topActionsEl.innerHTML = `<li class="text-slate-500 text-sm text-center py-4">No pending tasks found.</li>`;
        }
    }
    
    async function generateBrief() {
        const btn = document.querySelector('button[onclick="generateBrief()"]');
        btn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Analyzing...`;
        btn.disabled = true;
        
        document.getElementById('brief-content').innerHTML = `
            <div class="flex items-center gap-3 text-indigo-600 font-medium">
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                AI is analyzing your business data...
            </div>
        `;
        try {
            const res = await apiCall('/ai/daily-brief');
            document.getElementById('brief-content').innerText = res.text || res.error || "No response";
            showToast('Brief generated successfully');
        } catch(e) {
            document.getElementById('brief-content').innerText = "Failed to generate brief.";
        } finally {
            btn.innerHTML = `<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg> Regenerate Brief`;
            btn.disabled = false;
        }
    }

    document.addEventListener('DOMContentLoaded', loadDashboard);
</script>
"""

final_html = base_layout.format(
    title="Dashboard", 
    page_title="Dashboard", 
    header_extra="", 
    content=html_content, 
    scripts=scripts, 
    modals=""
)

write_file("dashboard.html", final_html)
print("Dashboard rebuilt.")
