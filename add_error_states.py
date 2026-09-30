import re

def update_error_state(filename, table_id, colspan):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we already have the error state to avoid double writing
    if 'Unable to load' in content:
        print(f"Skipping {filename}, already has error state.")
        return

    # Replace catch block
    catch_pattern = r'\} catch \(e\) \{\s*console\.error\(e\);\s*\}'
    
    error_html = f"document.getElementById('{table_id}').innerHTML = '<tr><td colspan=\"{colspan}\" class=\"px-6 py-8 text-center text-red-500\">Unable to load data. <button onclick=\"location.reload()\" class=\"text-primary underline hover:text-primaryHover ml-2\">Retry</button></td></tr>';"
    
    replacement = f"}} catch (e) {{\n            console.error(e);\n            {error_html}\n        }}"
    
    new_content = re.sub(catch_pattern, replacement, content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {filename}")

update_error_state('frontend/projects.html', 'projects-table', 5)
update_error_state('frontend/tasks.html', 'tasks-table', 7)
update_error_state('frontend/clients.html', 'clients-table', 5)
update_error_state('frontend/leads.html', 'leads-table', 6)

