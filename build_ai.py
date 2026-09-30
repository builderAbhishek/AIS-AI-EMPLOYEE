import os
from build_ui import write_file, base_layout

html_content = """
<div class="h-[calc(100vh-10rem)] flex bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    
    <!-- Chat Sidebar -->
    <div class="w-72 border-r border-slate-200 bg-slate-50 flex flex-col hidden md:flex shrink-0">
        <div class="p-4 border-b border-slate-200 flex justify-between items-center bg-white shrink-0">
            <h2 class="font-semibold text-slate-800">Conversations</h2>
            <button onclick="newChat()" class="text-primary hover:text-primaryHover p-1 rounded-md hover:bg-slate-100 transition-colors" title="New Chat">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            </button>
        </div>
        <div class="p-3 border-b border-slate-200 bg-white shrink-0">
            <div class="relative">
                <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                <input type="text" id="chatSearch" placeholder="Search chats..." class="w-full pl-9 pr-3 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" oninput="filterChats()">
            </div>
        </div>
        <div class="flex-1 overflow-y-auto p-2 space-y-1" id="chat-list">
            <!-- Chats loaded here -->
            <div class="text-center text-slate-400 text-sm py-4">Loading chats...</div>
        </div>
    </div>

    <!-- Chat Main Area -->
    <div class="flex-1 flex flex-col relative">
        <div class="absolute inset-0 flex flex-col">
            <!-- Chat Header -->
            <div id="active-chat-header" class="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6 shrink-0 hidden">
                <div class="flex items-center gap-3 font-medium text-slate-800" id="active-chat-title">
                    Loading...
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="exportChat('txt')" class="text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-md transition-colors">TXT</button>
                    <button onclick="exportChat('json')" class="text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-md transition-colors">JSON</button>
                    <button onclick="deleteCurrentChat()" class="text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-md transition-colors border border-red-200">Delete</button>
                </div>
            </div>

            <!-- Messages Area -->
            <div class="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50" id="chat-messages">
                <!-- Messages -->
            </div>

            <!-- Input Area -->
            <div class="p-4 bg-white border-t border-slate-200 shrink-0">
                <div class="max-w-4xl mx-auto relative flex items-end gap-2">
                    <textarea id="chatInput" rows="1" placeholder="Ask your AI Employee (Shift+Enter for newline)..." 
                        class="w-full resize-none py-3 pl-4 pr-12 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-sm leading-relaxed max-h-32 shadow-sm"
                        oninput="this.style.height = ''; this.style.height = Math.min(this.scrollHeight, 128) + 'px'"></textarea>
                    <button id="sendBtn" onclick="sendMessage()" class="absolute right-2 bottom-2 p-2 bg-primary text-white rounded-lg hover:bg-primaryHover transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                    </button>
                </div>
                <div class="text-center mt-2 text-[10px] text-slate-400 font-medium">AIS AI Employee can access your live CRM data. Planning is read-only.</div>
            </div>
        </div>
    </div>
</div>
"""

scripts = """
<script>
    let currentChatId = null;
    let allChats = [];

    function formatAIResponse(text) {
        if (!text) return '';
        let formatted = text
            .replace(/\\n/g, '\\n')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
            .replace(/^\\* (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*?<\\/li>(?:\\n)?)+/gs, match => `<ul class="list-disc pl-5 my-2 space-y-1">${match.replace(/\\n/g, '')}</ul>`)
            .replace(/\\n/g, '<br>');
        return formatted;
    }

    async function loadChats() {
        allChats = await apiCall('/chats/');
        renderChatList(allChats);
        
        if (allChats.length > 0 && !currentChatId) {
            selectChat(allChats[0].id);
        } else if (allChats.length === 0) {
            newChat();
        }
    }

    function renderChatList(chats) {
        const list = document.getElementById('chat-list');
        list.innerHTML = '';
        if(chats.length === 0) {
            list.innerHTML = '<div class="text-center text-slate-400 text-sm py-4">No conversations found.</div>';
            return;
        }
        chats.forEach(c => {
            const isActive = currentChatId === c.id;
            const div = document.createElement('div');
            div.className = `px-3 py-2.5 rounded-lg text-sm cursor-pointer transition-colors whitespace-nowrap overflow-hidden text-ellipsis border ${isActive ? 'bg-primary/5 border-primary/20 text-primary font-medium shadow-sm' : 'hover:bg-slate-100 text-slate-700 border-transparent'}`;
            div.textContent = c.title || 'New Chat';
            div.onclick = () => selectChat(c.id);
            list.appendChild(div);
        });
    }

    function filterChats() {
        const query = document.getElementById('chatSearch').value.toLowerCase();
        const filtered = allChats.filter(c => (c.title || '').toLowerCase().includes(query));
        renderChatList(filtered);
    }

    async function newChat() {
        const chat = await apiCall('/chats/', 'POST', {content: ''});
        currentChatId = chat.id;
        document.getElementById('chat-messages').innerHTML = `
            <div class="flex gap-4">
                <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0 border border-indigo-200">
                    <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
                <div class="flex-1 bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700">
                    Hello! I am your AIS AI Employee. How can I help you today?
                </div>
            </div>`;
        loadChats();
    }

    async function selectChat(id) {
        currentChatId = id;
        renderChatList(allChats); // Update active class quickly
        
        const data = await apiCall(`/chats/${id}`);
        
        document.getElementById('active-chat-header').classList.remove('hidden');
        document.getElementById('active-chat-title').textContent = data.chat.title;
        
        const msgs = document.getElementById('chat-messages');
        msgs.innerHTML = '';

        if (data.messages.length === 0) {
            msgs.innerHTML = `
            <div class="flex gap-4">
                <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0 border border-indigo-200">
                    <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
                <div class="flex-1 bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700">
                    Hello! I am your AIS AI Employee. How can I help you today?
                </div>
            </div>`;
        } else {
            data.messages.forEach(m => appendMessage(m.role, m.content, m.metadata_json));
        }
        msgs.scrollTop = msgs.scrollHeight;
    }
    
    function appendMessage(role, content, metadata = null) {
        const msgs = document.getElementById('chat-messages');
        const wrapper = document.createElement('div');
        wrapper.className = 'flex gap-4 ' + (role === 'user' ? 'flex-row-reverse' : '');
        
        let avatar = '';
        let bubbleClass = '';
        let formattedContent = '';
        
        if (role === 'user') {
            avatar = `<div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center shrink-0 text-white font-bold text-xs shadow-sm">You</div>`;
            bubbleClass = 'bg-primary text-white border-primary rounded-tr-none shadow-sm';
            formattedContent = content.replace(/\\n/g, '<br>');
        } else {
            avatar = `<div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0 border border-indigo-200"><svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg></div>`;
            bubbleClass = 'bg-white border-slate-200 text-slate-700 rounded-tl-none shadow-sm';
            formattedContent = formatAIResponse(content);
        }
        
        wrapper.innerHTML = `
            ${avatar}
            <div class="max-w-[85%] border p-4 rounded-2xl ${bubbleClass} text-sm leading-relaxed prose prose-sm max-w-none">
                ${formattedContent}
            </div>
        `;
        msgs.appendChild(wrapper);
    }

    async function sendMessage() {
        if (!currentChatId) await newChat();

        const input = document.getElementById('chatInput');
        const btn = document.getElementById('sendBtn');
        const text = input.value.trim();
        if (!text) return;

        appendMessage('user', text);
        input.value = '';
        input.style.height = '';
        btn.disabled = true;

        const msgs = document.getElementById('chat-messages');
        const loadingId = 'loading-' + Date.now();
        const loadingWrapper = document.createElement('div');
        loadingWrapper.id = loadingId;
        loadingWrapper.className = 'flex gap-4';
        loadingWrapper.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0 border border-indigo-200"><svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg></div>
            <div class="border border-slate-200 p-4 rounded-2xl bg-white rounded-tl-none shadow-sm text-sm text-slate-500 font-medium flex items-center gap-2">
                <svg class="animate-spin h-4 w-4 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                AI is thinking...
            </div>
        `;
        msgs.appendChild(loadingWrapper);
        msgs.scrollTop = msgs.scrollHeight;

        try {
            const res = await apiCall(`/chats/${currentChatId}/messages`, 'POST', { content: text });
            document.getElementById(loadingId).remove();

            let finalOutput = '';
            if (res.actions && res.actions.length > 0) {
                finalOutput += `<div class="mb-3 p-3 bg-green-50 text-green-800 border border-green-200 rounded-lg text-xs font-semibold font-mono">`;
                finalOutput += res.actions.join('<br>');
                finalOutput += `</div>`;
            }
            finalOutput += res.text;
            
            appendMessage('model', finalOutput);
            msgs.scrollTop = msgs.scrollHeight;
            loadChats(); // Update title if it changed
        } catch(e) {
            document.getElementById(loadingId).remove();
            appendMessage('model', '⚠️ Request failed. Please check the connection.');
        } finally {
            btn.disabled = false;
            input.focus();
        }
    }

    document.getElementById('chatInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function deleteCurrentChat() {
        if (!currentChatId) return;
        confirmAction("Delete this conversation? Related CRM data will NOT be deleted.", async () => {
            await apiCall(`/chats/${currentChatId}`, 'DELETE');
            showToast("Conversation deleted.");
            currentChatId = null;
            document.getElementById('active-chat-header').classList.add('hidden');
            document.getElementById('chat-messages').innerHTML = '';
            loadChats();
        });
    }

    async function exportChat(format) {
        if (!currentChatId) return alert("No active chat.");
        const data = await apiCall(`/chats/${currentChatId}`);
        if (format === 'json') {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat_${currentChatId}.json`;
            a.click();
        } else {
            let txt = `Chat: ${data.chat.title}\\n\\n`;
            data.messages.forEach(m => txt += `[${m.role.toUpperCase()}] ${m.created_at}\\n${m.content}\\n\\n`);
            const blob = new Blob([txt], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat_${currentChatId}.txt`;
            a.click();
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        loadChats();
    });
</script>
"""

final_html = base_layout.format(
    title="AI Employee", 
    page_title="AI Employee", 
    header_extra="", 
    content=html_content, 
    scripts=scripts, 
    modals=""
)

write_file("ai.html", final_html)
print("AI Employee rebuilt.")
