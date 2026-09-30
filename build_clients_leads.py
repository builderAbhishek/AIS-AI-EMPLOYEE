import os
from build_ui import write_file, base_layout

# --- CLIENTS ---
clients_html = """
<div class="mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
    <div class="relative w-full md:w-96">
        <svg class="w-5 h-5 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="searchInput" placeholder="Search clients..." class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" oninput="loadClients()">
    </div>
    <button onclick="openModal('addClientModal')" class="w-full md:w-auto bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primaryHover transition-colors flex items-center justify-center gap-2 shadow-sm">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        New Client
    </button>
</div>

<div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-slate-50 border-b border-slate-200 text-slate-500 text-sm font-semibold uppercase tracking-wider">
                    <th class="px-6 py-4">Business Name</th>
                    <th class="px-6 py-4">Contact</th>
                    <th class="px-6 py-4">Services</th>
                    <th class="px-6 py-4">Status</th>
                    <th class="px-6 py-4 text-right">Actions</th>
                </tr>
            </thead>
            <tbody id="clients-table" class="divide-y divide-slate-200 text-sm text-slate-700">
                <tr><td colspan="5" class="px-6 py-8 text-center text-slate-500">Loading clients...</td></tr>
            </tbody>
        </table>
    </div>
</div>
"""

clients_modals = """
<!-- Add Client Modal -->
<div id="addClientModal" class="modal fixed inset-0 bg-slate-900/50 z-50 justify-center items-center p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-slate-800">Add New Client</h3>
            <button onclick="closeModal('addClientModal')" class="text-slate-400 hover:text-slate-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="p-6 overflow-y-auto">
            <form id="addClientForm" onsubmit="addClient(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Business Name</label>
                    <input type="text" id="business_name" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Contact Name</label>
                        <input type="text" id="contact_name" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                        <input type="text" id="phone" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
                    <input type="email" id="email" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Services</label>
                    <input type="text" id="services" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
                    <select id="status" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                        <option value="ACTIVE">Active</option>
                        <option value="INACTIVE">Inactive</option>
                    </select>
                </div>
                <div class="pt-4 border-t border-slate-200 flex justify-end gap-3">
                    <button type="button" onclick="closeModal('addClientModal')" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primaryHover transition-colors shadow-sm">Create Client</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""

clients_scripts = """
<script>
    async function loadClients() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        try {
            const data = await apiCall('/clients/');
            const tbody = document.getElementById('clients-table');
            tbody.innerHTML = '';
            
            const filtered = data.filter(c => c.business_name.toLowerCase().includes(query) || (c.contact_name && c.contact_name.toLowerCase().includes(query)));
            
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-slate-500">No clients found.</td></tr>';
                return;
            }

            filtered.forEach(c => {
                let statusBadge = c.status === 'ACTIVE' 
                    ? '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20">Active</span>' 
                    : '<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-600/20">Inactive</span>';

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50/50 transition-colors">
                        <td class="px-6 py-4 font-medium text-slate-900">${c.business_name}</td>
                        <td class="px-6 py-4">
                            <div class="text-slate-800">${c.contact_name || '-'}</div>
                            <div class="text-xs text-slate-500">${c.phone || ''}</div>
                        </td>
                        <td class="px-6 py-4 text-slate-600">${c.services || '-'}</td>
                        <td class="px-6 py-4">${statusBadge}</td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="deleteClient(${c.id})" class="text-slate-400 hover:text-red-600 p-1.5 rounded-md hover:bg-red-50 transition-colors" title="Delete">
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

    async function addClient(e) {
        e.preventDefault();
        const payload = {
            business_name: document.getElementById('business_name').value,
            contact_name: document.getElementById('contact_name').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            services: document.getElementById('services').value,
            status: document.getElementById('status').value
        };
        await apiCall('/clients/', 'POST', payload);
        closeModal('addClientModal');
        document.getElementById('addClientForm').reset();
        showToast('Client created');
        loadClients();
    }

    async function deleteClient(id) {
        confirmAction("Delete this client? This might affect related projects.", async () => {
            await apiCall(`/clients/${id}`, 'DELETE');
            showToast('Client deleted');
            loadClients();
        });
    }

    document.addEventListener('DOMContentLoaded', loadClients);
</script>
"""

write_file("clients.html", base_layout.format(
    title="Clients", page_title="Clients", header_extra="", 
    content=clients_html, scripts=clients_scripts, modals=clients_modals
))


# --- LEADS ---
leads_html = """
<div class="mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
    <div class="relative w-full md:w-96">
        <svg class="w-5 h-5 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="searchInput" placeholder="Search leads..." class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" oninput="loadLeads()">
    </div>
    <div class="flex gap-2 w-full md:w-auto">
        <select id="statusFilter" class="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 text-sm bg-white" onchange="loadLeads()">
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="CONTACTED">Contacted</option>
            <option value="QUALIFIED">Qualified</option>
            <option value="PROPOSAL">Proposal</option>
            <option value="WON">Won</option>
            <option value="LOST">Lost</option>
        </select>
        <button onclick="openModal('addLeadModal')" class="w-full md:w-auto bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primaryHover transition-colors flex items-center justify-center gap-2 shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            New Lead
        </button>
    </div>
</div>

<div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-slate-50 border-b border-slate-200 text-slate-500 text-sm font-semibold uppercase tracking-wider">
                    <th class="px-6 py-4">Business / Contact</th>
                    <th class="px-6 py-4">Interest</th>
                    <th class="px-6 py-4">Status & Priority</th>
                    <th class="px-6 py-4 text-right">Actions</th>
                </tr>
            </thead>
            <tbody id="leads-table" class="divide-y divide-slate-200 text-sm text-slate-700">
                <tr><td colspan="4" class="px-6 py-8 text-center text-slate-500">Loading leads...</td></tr>
            </tbody>
        </table>
    </div>
</div>
"""

leads_modals = """
<!-- Add Lead Modal -->
<div id="addLeadModal" class="modal fixed inset-0 bg-slate-900/50 z-50 justify-center items-center p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-slate-800">Add New Lead</h3>
            <button onclick="closeModal('addLeadModal')" class="text-slate-400 hover:text-slate-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="p-6 overflow-y-auto">
            <form id="addLeadForm" onsubmit="addLead(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Business Name</label>
                    <input type="text" id="business_name" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Contact Name</label>
                        <input type="text" id="contact_name" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                        <input type="text" id="phone" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Service Interest</label>
                    <input type="text" id="service_interest" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
                        <select id="status" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                            <option value="NEW">New</option>
                            <option value="CONTACTED">Contacted</option>
                            <option value="QUALIFIED">Qualified</option>
                            <option value="PROPOSAL">Proposal</option>
                            <option value="WON">Won</option>
                            <option value="LOST">Lost</option>
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
                    <label class="block text-sm font-medium text-slate-700 mb-1">Source</label>
                    <input type="text" id="source" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary">
                </div>
                <div class="pt-4 border-t border-slate-200 flex justify-end gap-3">
                    <button type="button" onclick="closeModal('addLeadModal')" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primaryHover transition-colors shadow-sm">Create Lead</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""

leads_scripts = """
<script>
    async function loadLeads() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        try {
            const data = await apiCall('/leads/');
            const tbody = document.getElementById('leads-table');
            tbody.innerHTML = '';
            
            const filtered = data.filter(l => {
                const matchQuery = l.business_name.toLowerCase().includes(query) || (l.contact_name && l.contact_name.toLowerCase().includes(query));
                const matchStatus = statusFilter ? l.status === statusFilter : true;
                return matchQuery && matchStatus;
            });
            
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-slate-500">No leads found.</td></tr>';
                return;
            }

            filtered.forEach(l => {
                let statusColor = 'bg-slate-100 text-slate-700 ring-slate-600/20';
                if(l.status === 'NEW') statusColor = 'bg-blue-50 text-blue-700 ring-blue-600/20';
                if(l.status === 'WON') statusColor = 'bg-green-50 text-green-700 ring-green-600/20';
                if(l.status === 'LOST') statusColor = 'bg-red-50 text-red-700 ring-red-600/20';
                if(l.status === 'QUALIFIED') statusColor = 'bg-purple-50 text-purple-700 ring-purple-600/20';
                
                let priorityClass = l.priority === 'HIGH' ? 'text-red-600 font-bold' : (l.priority === 'MEDIUM' ? 'text-amber-600 font-semibold' : 'text-slate-500');

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50/50 transition-colors">
                        <td class="px-6 py-4">
                            <div class="font-medium text-slate-900">${l.business_name}</div>
                            <div class="text-sm text-slate-500">${l.contact_name || '-'} ${l.phone ? ' | '+l.phone : ''}</div>
                        </td>
                        <td class="px-6 py-4 text-slate-600">
                            <div>${l.service_interest || '-'}</div>
                            <div class="text-xs text-slate-400">Src: ${l.source || 'Unknown'}</div>
                        </td>
                        <td class="px-6 py-4">
                            <div class="flex flex-col gap-1 items-start">
                                <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ring-1 ring-inset ${statusColor}">${l.status}</span>
                                <span class="text-[10px] ${priorityClass}">${l.priority} PRIORITY</span>
                            </div>
                        </td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="deleteLead(${l.id})" class="text-slate-400 hover:text-red-600 p-1.5 rounded-md hover:bg-red-50 transition-colors" title="Delete">
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

    async function addLead(e) {
        e.preventDefault();
        const payload = {
            business_name: document.getElementById('business_name').value,
            contact_name: document.getElementById('contact_name').value,
            phone: document.getElementById('phone').value,
            service_interest: document.getElementById('service_interest').value,
            status: document.getElementById('status').value,
            priority: document.getElementById('priority').value,
            source: document.getElementById('source').value
        };
        await apiCall('/leads/', 'POST', payload);
        closeModal('addLeadModal');
        document.getElementById('addLeadForm').reset();
        showToast('Lead created');
        loadLeads();
    }

    async function deleteLead(id) {
        confirmAction("Delete this lead?", async () => {
            await apiCall(`/leads/${id}`, 'DELETE');
            showToast('Lead deleted');
            loadLeads();
        });
    }

    document.addEventListener('DOMContentLoaded', loadLeads);
</script>
"""

write_file("leads.html", base_layout.format(
    title="Leads", page_title="Leads", header_extra="", 
    content=leads_html, scripts=leads_scripts, modals=leads_modals
))

print("Clients and Leads rebuilt.")
