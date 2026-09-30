import os
from build_ui import write_file, base_layout

html_content = """
<div class="mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
    <div class="relative w-full md:w-96">
        <svg class="w-5 h-5 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="searchInput" placeholder="Search tasks..." class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" oninput="loadTasks()">
    </div>
    <div class="flex gap-2 w-full md:w-auto">
        <select id="statusFilter" class="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 text-sm bg-white" onchange="loadTasks()">
            <option value="">All Statuses</option>
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="DONE">Done</option>
        </select>
        <button onclick="openModal('addTaskModal')" class="w-full md:w-auto bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primaryHover transition-colors flex items-center justify-center gap-2 shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            New Task
        </button>
    </div>
</div>

<div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-slate-50 border-b border-slate-200 text-slate-500 text-sm font-semibold uppercase tracking-wider">
                    <th class="px-6 py-4">ID</th>
                    <th class="px-6 py-4 w-1/3">Task</th>
                    <th class="px-6 py-4">Project</th>
                    <th class="px-6 py-4">Status</th>
                    <th class="px-6 py-4">Due Date</th>
                    <th class="px-6 py-4 text-right">Actions</th>
                </tr>
            </thead>
            <tbody id="tasks-table" class="divide-y divide-slate-200 text-sm text-slate-700">
                <tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">Loading tasks...</td></tr>
            </tbody>
        </table>
    </div>
</div>
"""

modals = """
<!-- Add Task Modal -->
<div id="addTaskModal" class="modal fixed inset-0 bg-slate-900/50 z-50 justify-center items-center p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-slate-800">Add New Task</h3>
            <button onclick="closeModal('addTaskModal')" class="text-slate-400 hover:text-slate-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="p-6 overflow-y-auto">
            <form id="addTaskForm" onsubmit="addTask(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Title</label>
                    <input type="text" id="title" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Project</label>
                    <select id="project_id" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                        <option value="">No Project</option>
                    </select>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
                        <select id="status" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                            <option value="TODO">To Do</option>
                            <option value="IN_PROGRESS">In Progress</option>
                            <option value="DONE">Done</option>
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
                    <label class="block text-sm font-medium text-slate-700 mb-1">Due Date</label>
                    <input type="datetime-local" id="deadline" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
                    <textarea id="description" rows="3" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"></textarea>
                </div>
                <div class="pt-4 border-t border-slate-200 flex justify-end gap-3">
                    <button type="button" onclick="closeModal('addTaskModal')" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primaryHover transition-colors shadow-sm">Create Task</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""

scripts = """
<script>
    async function loadTasks() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        try {
            const data = await apiCall('/tasks/');
            const projects = await apiCall('/projects/');
            const projectMap = {};
            projects.forEach(p => projectMap[p.id] = p.project_name);
            
            const tbody = document.getElementById('tasks-table');
            tbody.innerHTML = '';
            
            const filtered = data.filter(t => {
                const matchQuery = t.title.toLowerCase().includes(query);
                const matchStatus = statusFilter ? t.status === statusFilter : true;
                return matchQuery && matchStatus;
            });
            
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">No tasks found.</td></tr>';
                return;
            }

            const now = new Date();

            filtered.forEach(t => {
                let statusBadge = '';
                if(t.status === 'DONE') statusBadge = '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20">Done</span>';
                else if(t.status === 'IN_PROGRESS') statusBadge = '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20">In Progress</span>';
                else statusBadge = '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-600/20">To Do</span>';
                
                let priorityClass = t.priority === 'HIGH' ? 'text-red-600 font-bold' : (t.priority === 'MEDIUM' ? 'text-amber-600 font-semibold' : 'text-slate-500');

                let dueStr = '-';
                let overdueClass = 'text-slate-600';
                if (t.deadline) {
                    const d = new Date(t.deadline);
                    dueStr = d.toLocaleDateString();
                    if (d < now && t.status !== 'DONE') {
                        dueStr = `<span class="text-red-600 font-semibold flex items-center gap-1"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg> ${dueStr} (Overdue)</span>`;
                    }
                }

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50/50 transition-colors">
                        <td class="px-6 py-4 font-mono text-xs text-slate-500">#${t.id}</td>
                        <td class="px-6 py-4 font-medium text-slate-900">
                            ${t.title}
                            <div class="text-[10px] mt-1 ${priorityClass}">${t.priority} PRIORITY</div>
                        </td>
                        <td class="px-6 py-4 text-slate-600 text-sm">${t.project_id ? (projectMap[t.project_id] || 'Unknown') : '-'}</td>
                        <td class="px-6 py-4">${statusBadge}</td>
                        <td class="px-6 py-4 text-sm">${dueStr}</td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="deleteTask(${t.id})" class="text-slate-400 hover:text-red-600 p-1.5 rounded-md hover:bg-red-50 transition-colors" title="Delete">
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

    async function addTask(e) {
        e.preventDefault();
        const payload = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            status: document.getElementById('status').value,
            priority: document.getElementById('priority').value,
            deadline: document.getElementById('deadline').value || null
        };
        const p_id = document.getElementById('project_id').value;
        if(p_id) payload.project_id = parseInt(p_id);

        await apiCall('/tasks/', 'POST', payload);
        closeModal('addTaskModal');
        document.getElementById('addTaskForm').reset();
        showToast('Task created');
        loadTasks();
    }

    async function deleteTask(id) {
        confirmAction("Delete this task?", async () => {
            await apiCall(`/tasks/${id}`, 'DELETE');
            showToast('Task deleted');
            loadTasks();
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        loadDropdown('/projects/', 'project_id', 'project_name', 'id');
        loadTasks();
    });
</script>
"""

final_html = base_layout.format(
    title="Tasks", 
    page_title="Tasks", 
    header_extra="", 
    content=html_content, 
    scripts=scripts, 
    modals=modals
)

write_file("tasks.html", final_html)
print("Tasks rebuilt.")
