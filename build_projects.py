import os
from build_ui import write_file, base_layout

html_content = """
<div class="mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
    <div class="relative w-full md:w-96">
        <svg class="w-5 h-5 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="searchInput" placeholder="Search projects..." class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" oninput="loadProjects()">
    </div>
    <button onclick="openModal('addProjectModal')" class="w-full md:w-auto bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primaryHover transition-colors flex items-center justify-center gap-2 shadow-sm">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        New Project
    </button>
</div>

<div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-slate-50 border-b border-slate-200 text-slate-500 text-sm font-semibold uppercase tracking-wider">
                    <th class="px-6 py-4">Project Name</th>
                    <th class="px-6 py-4">Client</th>
                    <th class="px-6 py-4">Status & Progress</th>
                    <th class="px-6 py-4">Priority</th>
                    <th class="px-6 py-4 text-right">Actions</th>
                </tr>
            </thead>
            <tbody id="projects-table" class="divide-y divide-slate-200 text-sm text-slate-700">
                <tr><td colspan="5" class="px-6 py-8 text-center text-slate-500">Loading projects...</td></tr>
            </tbody>
        </table>
    </div>
</div>
"""

modals = """
<!-- Add Project Modal -->
<div id="addProjectModal" class="modal fixed inset-0 bg-slate-900/50 z-50 justify-center items-center p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-slate-800">Add New Project</h3>
            <button onclick="closeModal('addProjectModal')" class="text-slate-400 hover:text-slate-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="p-6 overflow-y-auto">
            <form id="addProjectForm" onsubmit="addProject(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Project Name</label>
                    <input type="text" id="project_name" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Client</label>
                    <select id="client_id" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"></select>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
                        <select id="status" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                            <option value="PLANNING">Planning</option>
                            <option value="IN_PROGRESS">In Progress</option>
                            <option value="ON_HOLD">On Hold</option>
                            <option value="COMPLETED">Completed</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Priority</label>
                        <select id="priority" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                            <option value="LOW">Low</option>
                            <option value="MEDIUM" selected>Medium</option>
                            <option value="HIGH">High</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
                    <textarea id="description" rows="3" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"></textarea>
                </div>
                <div class="pt-4 border-t border-slate-200 flex justify-end gap-3">
                    <button type="button" onclick="closeModal('addProjectModal')" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primaryHover transition-colors shadow-sm">Create Project</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""

scripts = """
<script>
    async function loadProjects() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        try {
            const data = await apiCall('/projects/');
            const clients = await apiCall('/clients/');
            const clientMap = {};
            clients.forEach(c => clientMap[c.id] = c.business_name);
            
            const tbody = document.getElementById('projects-table');
            tbody.innerHTML = '';
            
            const filtered = data.filter(p => p.project_name.toLowerCase().includes(query));
            
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-slate-500">No projects found.</td></tr>';
                return;
            }

            filtered.forEach(p => {
                let statusBadge = '';
                if(p.status === 'COMPLETED') statusBadge = '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20">Completed</span>';
                else if(p.status === 'IN_PROGRESS') statusBadge = '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20">In Progress</span>';
                else if(p.status === 'PLANNING') statusBadge = '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-50 text-purple-700 ring-1 ring-inset ring-purple-600/20">Planning</span>';
                else statusBadge = `<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-slate-50 text-slate-700 ring-1 ring-inset ring-slate-600/20">${p.status}</span>`;
                
                let priorityClass = p.priority === 'HIGH' ? 'text-red-600 font-bold' : (p.priority === 'MEDIUM' ? 'text-amber-600 font-semibold' : 'text-slate-500');

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50/50 transition-colors">
                        <td class="px-6 py-4 font-medium text-slate-900">${p.project_name}</td>
                        <td class="px-6 py-4 text-slate-600">${clientMap[p.client_id] || 'Unknown'}</td>
                        <td class="px-6 py-4">
                            <div class="flex flex-col gap-2">
                                <div>${statusBadge}</div>
                                <div class="w-full bg-slate-200 rounded-full h-1.5">
                                  <div class="bg-primary h-1.5 rounded-full" style="width: ${p.progress}%"></div>
                                </div>
                                <div class="text-[10px] text-slate-400 font-medium">${p.progress}%</div>
                            </div>
                        </td>
                        <td class="px-6 py-4 ${priorityClass}">${p.priority}</td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="deleteProject(${p.id})" class="text-slate-400 hover:text-red-600 p-1.5 rounded-md hover:bg-red-50 transition-colors" title="Delete">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                            </button>
                        </td>
                    </tr>
                `;
            });
        } catch (e) {
            console.error(e);
        }
    }

    async function addProject(e) {
        e.preventDefault();
        const payload = {
            project_name: document.getElementById('project_name').value,
            client_id: parseInt(document.getElementById('client_id').value),
            description: document.getElementById('description').value,
            status: document.getElementById('status').value,
            priority: document.getElementById('priority').value,
            progress: 0
        };
        await apiCall('/projects/', 'POST', payload);
        closeModal('addProjectModal');
        document.getElementById('addProjectForm').reset();
        showToast('Project created successfully');
        loadProjects();
    }

    async function deleteProject(id) {
        confirmAction("Delete this project?", async () => {
            await apiCall(`/projects/${id}`, 'DELETE');
            showToast('Project deleted');
            loadProjects();
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        loadDropdown('/clients/', 'client_id', 'business_name', 'id');
        loadProjects();
    });
</script>
"""

final_html = base_layout.format(
    title="Projects", 
    page_title="Projects", 
    header_extra="", 
    content=html_content, 
    scripts=scripts, 
    modals=modals
)

write_file("projects.html", final_html)
print("Projects rebuilt.")
