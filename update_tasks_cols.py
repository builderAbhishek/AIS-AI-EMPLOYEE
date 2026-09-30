import re

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\frontend\tasks.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update table headers
content = content.replace('<th class="px-6 py-4">Due Date</th>', '<th class="px-6 py-4">Due Date</th>\n                      <th class="px-6 py-4">Created Date</th>')

# Update table body row
# Previous:
# <td class="px-6 py-4 text-sm">${dueStr}</td>
# <td class="px-6 py-4 text-right">
# We insert created_at.
# Let's add parsing for created_at.
row_replace = """<td class="px-6 py-4 text-sm">${dueStr}</td>
                        <td class="px-6 py-4 text-sm text-slate-500">${t.created_at ? new Date(t.created_at).toLocaleDateString() : '-'}</td>
                        <td class="px-6 py-4 text-right">"""

content = content.replace('<td class="px-6 py-4 text-sm">${dueStr}</td>\n                        <td class="px-6 py-4 text-right">', row_replace)

# Also update the colspan in error state from 6 or 7 to 7
content = content.replace('colspan="6"', 'colspan="7"')

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\frontend\tasks.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated tasks.html with Created Date")
