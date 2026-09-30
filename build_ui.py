import os

base_layout = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AIS OS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#2563eb',
                        primaryHover: '#1d4ed8'
                    }}
                }}
            }}
        }}
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        /* Scrollbar styles */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #94a3b8; }}
        
        /* Modal */
        .modal {{ display: none; }}
        .modal.active {{ display: flex; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 flex h-screen overflow-hidden">

    <!-- Sidebar -->
    <div id="sidebar" class="w-64 bg-white border-r border-slate-200 flex-col hidden md:flex shrink-0"></div>

    <div class="flex-1 flex flex-col overflow-hidden relative">
        <!-- Header -->
        <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 z-10 relative">
            <div class="flex items-center gap-4">
                <button class="md:hidden text-slate-500 hover:text-slate-700" onclick="document.getElementById('sidebar').classList.toggle('hidden'); document.getElementById('sidebar').classList.toggle('absolute'); document.getElementById('sidebar').classList.toggle('h-full'); document.getElementById('sidebar').classList.toggle('z-50');">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
                <h1 class="text-xl font-semibold">{page_title}</h1>
            </div>
            <div class="flex items-center gap-4">
                {header_extra}
                <div id="mode-indicator" class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-slate-400"></div> Loading...
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="flex-1 overflow-y-auto p-4 md:p-8">
            <div class="max-w-6xl mx-auto w-full">
                {content}
            </div>
        </main>
        
        <!-- Toasts -->
        <div id="toast-container" class="fixed bottom-4 right-4 z-50 flex flex-col gap-2"></div>
    </div>

    {modals}

    <script src="assets/js/app.js"></script>
    {scripts}
</body>
</html>"""

def write_file(filename, html):
    with open(f"frontend/{filename}", "w", encoding="utf-8") as f:
        f.write(html)

print("Builder loaded")
