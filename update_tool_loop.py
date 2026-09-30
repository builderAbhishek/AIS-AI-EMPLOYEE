import re

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = """
        messages = [{"role": "system", "content": system_context}]
        for h in history:
            messages.append({"role": "user" if h["role"] == "user" else "assistant", "content": h.get("text", "")})
        messages.append({"role": "user", "content": prompt})
        
        final_text = ""
        try:
            payload["messages"] = messages
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method="POST")
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode())
                message = result.get("message", {})
                
                if message.get("tool_calls"):
                    messages.append(message)
                    for tool_call in message["tool_calls"]:
                        fn_name = tool_call["function"]["name"]
                        fn_args = tool_call["function"]["arguments"]
                        tool_result = {"success": False, "error": "Tool not found"}
                        if fn_name in tools_map:
                            try:
                                tool_result = tools_map[fn_name](**fn_args)
                            except Exception as e:
                                tool_result = {"success": False, "error": str(e)}
                        
                        messages.append({
                            "role": "tool",
                            "content": json.dumps(tool_result)
                        })
                    
                    # Second call to Ollama to get the actual answer
                    payload["messages"] = messages
                    req2 = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method="POST")
                    with urllib.request.urlopen(req2, timeout=300) as response2:
                        result2 = json.loads(response2.read().decode())
                        message2 = result2.get("message", {})
                        final_text = message2.get("content", "")
                        if not final_text or not str(final_text).strip():
                            final_text = "I have processed your request and updated the CRM based on the tool results."
                else:
                    final_text = message.get("content", "")
                    
                if chat_id:
                    db.add(models.Activity(action="AI_REQUEST_OLLAMA", entity_type="CHAT", entity_id=chat_id, description="Ollama Request completed"))
                    db.commit()
"""

# Replace the block
content = re.sub(
    r'        messages = \[\{"role": "system", "content": system_context\}\].*?db\.commit\(\)',
    new_logic.strip('\n'),
    content,
    flags=re.DOTALL
)

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated AI Provider with Tool Loop.")
