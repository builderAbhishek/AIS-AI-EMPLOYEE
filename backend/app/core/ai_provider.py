import json
import urllib.request
import urllib.error
import re
from datetime import datetime
from .config import settings
from ..database import models

VALID_PROJECT_STATUSES = ["PLANNING", "IN_PROGRESS", "COMPLETED", "ON_HOLD", "CANCELLED"]
VALID_TASK_STATUSES = ["TODO", "IN_PROGRESS", "DONE", "BACKLOG", "PLANNING", "Pending", "COMPLETED"]


class AIProvider:
    def __init__(self):
        pass

    def get_mode(self):
        return "ollama"

    def test_connection(self) -> dict:
        settings.reload()
        url = settings.OLLAMA_BASE_URL.rstrip('/') + "/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": "Reply with exactly: AIS Ollama connection successful",
            "stream": False
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                        headers={'Content-Type': 'application/json'}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                if "AIS Ollama connection successful" in result.get("response", ""):
                    return {"success": True, "message": "Connection successful", "model": settings.OLLAMA_MODEL}
                return {"success": False, "message": "Unexpected response"}
        except Exception as e:
            return {"success": False, "message": f"Ollama is not responding. Check if running on {settings.OLLAMA_BASE_URL}"}

    # ==================================================================
    # INTENT DETECTION
    # ==================================================================

    def _is_explicit_action(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()

        planning_words = ["plan", "suggest", "recommend", "batao", "dikhao", "how to", "break down", "list"]
        action_overrides = ["ab create", "save karo", "execute", "create task", "update", "mark", "change status"]
        if any(w in prompt_lower for w in planning_words) and not any(a in prompt_lower for a in action_overrides):
            return False

        action_words = [
            "create", "add", "insert", "save", "update", "execute",
            "do it", "karo", "kar do", "bana do", "mark",
            "change status", "complete karo", "completed karo",
            "done karo", "done mark", "completed mark",
        ]
        if any(w in prompt_lower for w in action_words):
            return True

        return False

    def _is_update_intent(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        update_phrases = [
            "update", "change status", "mark", "set status",
            "status update", "status change", "status completed",
            "status done", "ko completed", "completed karo",
            "completed kar do", "completed mark", "complete karo",
            "complete kar do", "done karo", "done kar do",
            "done mark", "ko done", "ko complete",
        ]
        return any(phrase in prompt_lower for phrase in update_phrases)

    def _detect_target_status(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        ordered_keywords = [
            ("in_progress", "IN_PROGRESS"),
            ("in progress", "IN_PROGRESS"),
            ("on_hold", "ON_HOLD"),
            ("on hold", "ON_HOLD"),
            ("to do", "TODO"),
            ("todo", "TODO"),
            ("completed", "COMPLETED"),
            ("complete", "COMPLETED"),
            ("done", "DONE"),
            ("planning", "PLANNING"),
            ("backlog", "BACKLOG"),
            ("cancelled", "CANCELLED"),
            ("canceled", "CANCELLED"),
            ("pending", "Pending"),
        ]
        for kw, status in ordered_keywords:
            if kw in prompt_lower:
                return status
        return None

    def _is_project_or_task(self, prompt: str) -> tuple:
        prompt_lower = prompt.lower()
        return ("project" in prompt_lower, "task" in prompt_lower)

    # ==================================================================
    # ENTITY RESOLUTION
    # ==================================================================

    # Words that are action/intent keywords, NOT entity names
    _NOISE_WORDS = {
        "update", "status", "completed", "complete", "done", "mark",
        "karo", "kar", "do", "kya", "hai", "ka", "ke", "ki", "ko",
        "project", "task", "batao", "dikhao", "details", "change",
        "set", "to", "the", "is", "and", "for", "me", "mein",
        "planning", "progress", "backlog", "cancelled", "pending",
        "in_progress", "todo",
    }

    def _clean_prompt_for_matching(self, prompt: str) -> str:
        """Remove action/intent keywords so only entity names remain."""
        words = prompt.lower().split()
        cleaned = [w for w in words if w not in self._NOISE_WORDS]
        return " ".join(cleaned)

    def _find_matching_entities(self, prompt: str, db) -> dict:
        prompt_lower = prompt.lower()
        search_text = self._clean_prompt_for_matching(prompt)
        results = {"clients": [], "projects": [], "tasks": []}

        # --- Match clients ---
        for c in db.query(models.Client).all():
            name_lower = c.business_name.lower()
            if name_lower in prompt_lower:
                results["clients"].append(c)
            else:
                significant = [w for w in name_lower.split() if len(w) > 3 and w not in self._NOISE_WORDS]
                if significant and all(w in search_text for w in significant):
                    results["clients"].append(c)

        matched_client_ids = {c.id for c in results["clients"]}

        # --- Match projects ---
        for p in db.query(models.Project).all():
            name_lower = p.project_name.lower()
            if name_lower in prompt_lower:
                results["projects"].append(p)
            else:
                significant = [w for w in name_lower.split() if len(w) > 3 and w not in self._NOISE_WORDS]
                if significant and all(w in search_text for w in significant):
                    results["projects"].append(p)

            if not any(pp.id == p.id for pp in results["projects"]):
                if p.client_id and p.client_id in matched_client_ids:
                    results["projects"].append(p)

        matched_project_ids = {p.id for p in results["projects"]}

        # --- Match tasks by project/client relationship ---
        if matched_project_ids:
            for t in db.query(models.Task).filter(models.Task.project_id.in_(matched_project_ids)).all():
                if not any(tt.id == t.id for tt in results["tasks"]):
                    results["tasks"].append(t)

        if matched_client_ids and not results["tasks"]:
            for t in db.query(models.Task).filter(models.Task.client_id.in_(matched_client_ids)).all():
                if not any(tt.id == t.id for tt in results["tasks"]):
                    results["tasks"].append(t)

        # --- Match tasks by title ---
        for t in db.query(models.Task).all():
            if t.title.lower() in prompt_lower and not any(tt.id == t.id for tt in results["tasks"]):
                results["tasks"].append(t)

        # --- Match task by ID (#20, Task 20, etc.) ---
        id_match = re.search(r'(?:task\s*#?\s*|#)(\d+)', prompt_lower)
        if id_match:
            tid = int(id_match.group(1))
            task = db.query(models.Task).filter(models.Task.id == tid).first()
            if task and not any(t.id == task.id for t in results["tasks"]):
                results["tasks"].append(task)

        return results

    def _format_crm_context(self, entities: dict, db) -> str:
        parts = []

        if entities["clients"]:
            parts.append("=== CLIENTS (from database) ===")
            for c in entities["clients"]:
                parts.append(
                    f"Client #{c.id}: {c.business_name} | Contact: {c.contact_person or 'N/A'} "
                    f"| Status: {c.status} | Services: {c.services or 'N/A'}"
                )

        if entities["projects"]:
            parts.append("\n=== PROJECTS (from database) ===")
            for p in entities["projects"]:
                client_name = "N/A"
                if p.client_id:
                    cl = db.query(models.Client).filter(models.Client.id == p.client_id).first()
                    if cl:
                        client_name = cl.business_name
                parts.append(
                    f"Project #{p.id}: {p.project_name} | Client: {client_name} "
                    f"| Status: {p.status} | Progress: {p.progress}% | Priority: {p.priority}"
                )

        if entities["tasks"]:
            parts.append("\n=== TASKS (from database) ===")
            for t in entities["tasks"]:
                project_name = "N/A"
                if t.project_id:
                    pr = db.query(models.Project).filter(models.Project.id == t.project_id).first()
                    if pr:
                        project_name = pr.project_name
                deadline_str = str(t.deadline) if t.deadline else "Not set"
                parts.append(
                    f"Task #{t.id}: {t.title} | Project: {project_name} "
                    f"| Status: {t.status} | Priority: {t.priority} | Deadline: {deadline_str}"
                )

        return "\n".join(parts) if parts else ""

    # ==================================================================
    # DATABASE WRITE + READ-BACK VERIFICATION
    # ==================================================================

    def _execute_project_update(self, project, new_status, db, actions_taken) -> dict:
        old_status = project.status

        if old_status == new_status:
            actions_taken.append(f"Project #{project.id} '{project.project_name}' already {new_status}")
            return {
                "success": True, "already_done": True,
                "project_id": project.id, "project_name": project.project_name,
                "status": old_status,
            }

        if new_status not in VALID_PROJECT_STATUSES:
            return {"success": False, "error": f"Invalid project status '{new_status}'. Valid: {', '.join(VALID_PROJECT_STATUSES)}"}

        try:
            project.status = new_status
            if new_status == "COMPLETED":
                project.progress = 100
            db.commit()

            # READ-BACK VERIFICATION
            db.refresh(project)
            if project.status != new_status:
                return {"success": False, "verified": False, "error": "Database verification failed after commit."}

            activity = models.Activity(
                action="UPDATE_PROJECT_STATUS", entity_type="PROJECT", entity_id=project.id,
                description=f"Project '{project.project_name}' status: {old_status} -> {new_status}"
            )
            db.add(activity)
            db.commit()

            actions_taken.append(f"Project #{project.id} '{project.project_name}': {old_status} -> {new_status}")
            return {
                "success": True, "verified": True,
                "project_id": project.id, "project_name": project.project_name,
                "old_status": old_status, "new_status": new_status,
                "progress": project.progress,
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

    def _execute_task_update(self, task, new_status, db, actions_taken) -> dict:
        old_status = task.status

        if old_status == new_status:
            actions_taken.append(f"Task #{task.id} '{task.title}' already {new_status}")
            return {
                "success": True, "already_done": True,
                "task_id": task.id, "title": task.title, "status": old_status,
            }

        try:
            task.status = new_status
            if new_status in ("DONE", "COMPLETED"):
                task.completed_at = datetime.utcnow()
            db.commit()

            # READ-BACK VERIFICATION
            db.refresh(task)
            if task.status != new_status:
                return {"success": False, "verified": False, "error": "Database verification failed after commit."}

            project_name = "N/A"
            if task.project_id:
                pr = db.query(models.Project).filter(models.Project.id == task.project_id).first()
                if pr:
                    project_name = pr.project_name

            activity = models.Activity(
                action="UPDATE_TASK_STATUS", entity_type="TASK", entity_id=task.id,
                description=f"Task '{task.title}' (Project: {project_name}) status: {old_status} -> {new_status}"
            )
            db.add(activity)
            db.commit()

            actions_taken.append(f"Task #{task.id} '{task.title}': {old_status} -> {new_status}")
            return {
                "success": True, "verified": True,
                "task_id": task.id, "title": task.title,
                "old_status": old_status, "new_status": new_status,
                "project_name": project_name,
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

    # ==================================================================
    # MAIN RESPONSE GENERATOR
    # ==================================================================

    def generate_response(self, prompt: str, system_context: str, history: list, db, chat_id: int = None) -> dict:
        settings.reload()

        actions_taken = []
        is_explicit = self._is_explicit_action(prompt)

        # ==============================================================
        # PHASE 1: SERVER-SIDE UPDATE EXECUTION
        # Handle update/write intents BEFORE calling Ollama.
        # This guarantees the LLM can never fake a write.
        # ==============================================================

        if is_explicit and self._is_update_intent(prompt):
            target_status = self._detect_target_status(prompt)
            if target_status:
                entities = self._find_matching_entities(prompt, db)
                is_project, is_task = self._is_project_or_task(prompt)

                result_text = self._handle_update(
                    entities, is_project, is_task, target_status, db, actions_taken
                )
                if result_text is not None:
                    return {"text": result_text, "actions": actions_taken,
                            "provider": "ollama", "model": settings.OLLAMA_MODEL}

        # ==============================================================
        # PHASE 2: CRM PRE-FETCH
        # Find relevant DB records BEFORE calling Ollama.
        # This gives the model actual data instead of hallucinating.
        # ==============================================================

        entities = self._find_matching_entities(prompt, db)
        crm_context = self._format_crm_context(entities, db)

        if crm_context:
            actions_taken.append(
                f"CRM lookup: {len(entities['clients'])} clients, "
                f"{len(entities['projects'])} projects, {len(entities['tasks'])} tasks"
            )

        # ==============================================================
        # PHASE 3: BUILD FOCUSED PROMPT + CALL OLLAMA
        # ==============================================================

        focused_system = self._build_focused_system_prompt(crm_context)

        # Tool functions (for Ollama tool-calling fallback)
        def create_task(title: str, priority: str, status: str,
                        description: str = "", project_id: int = None, client_id: int = None) -> dict:
            if not is_explicit:
                actions_taken.append("Action Blocked: Task creation requires explicit permission.")
                return {"blocked": True, "reason": "Write action requires explicit user instruction."}
            try:
                existing = db.query(models.Task).filter(
                    models.Task.title == title,
                    models.Task.project_id == project_id,
                    models.Task.client_id == client_id,
                ).first()
                if existing:
                    return {"success": False, "error": "Task already exists for this project."}

                task = models.Task(
                    title=title, description=description, project_id=project_id,
                    client_id=client_id, priority=priority, status=status,
                )
                db.add(task)
                db.commit()
                db.refresh(task)

                db.add(models.Activity(
                    action="TASK_CREATED_BY_AI", entity_type="TASK",
                    entity_id=task.id, description=f"AI created task: {task.title}",
                ))
                db.commit()

                actions_taken.append(f"Task #{task.id} Created: {title}")
                return {"success": True, "task_id": task.id, "title": task.title}
            except Exception as e:
                db.rollback()
                actions_taken.append(f"Failed to create: {title} ({e})")
                return {"success": False, "error": str(e)}

        def get_task(task_id: int) -> dict:
            try:
                task = db.query(models.Task).filter(models.Task.id == task_id).first()
                if not task:
                    actions_taken.append(f"Task #{task_id} not found")
                    return {"found": False, "message": f"Task #{task_id} not found in database."}
                project_name = None
                if task.project_id:
                    pr = db.query(models.Project).filter(models.Project.id == task.project_id).first()
                    if pr:
                        project_name = pr.project_name
                actions_taken.append(f"Looked up Task #{task_id}")
                return {
                    "found": True, "id": task.id, "title": task.title,
                    "project_id": task.project_id, "project_name": project_name,
                    "priority": task.priority, "status": task.status,
                    "due_date": str(task.deadline) if task.deadline else "Not set",
                    "created_at": str(task.created_at) if task.created_at else "Not set",
                    "description": task.description,
                }
            except Exception as e:
                return {"found": False, "error": str(e)}

        def search_crm(query: str) -> dict:
            try:
                query_lower = query.lower()
                res = {"clients": [], "projects": [], "tasks": []}

                for c in db.query(models.Client).all():
                    if query_lower in c.business_name.lower() or query_lower in str(c.id):
                        res["clients"].append({"id": c.id, "name": c.business_name, "services": c.services, "status": c.status})

                for p in db.query(models.Project).all():
                    if (query_lower in p.project_name.lower()
                            or query_lower in str(p.id)
                            or (p.client_id and any(c["id"] == p.client_id for c in res["clients"]))):
                        res["projects"].append({"id": p.id, "name": p.project_name, "client_id": p.client_id,
                                                "status": p.status, "progress": p.progress, "priority": p.priority})

                for t in db.query(models.Task).all():
                    if (query_lower in t.title.lower()
                            or query_lower in str(t.id)
                            or (t.project_id and any(p["id"] == t.project_id for p in res["projects"]))):
                        res["tasks"].append({"id": t.id, "title": t.title, "project_id": t.project_id,
                                             "status": t.status, "priority": t.priority,
                                             "deadline": str(t.deadline)})

                actions_taken.append(f"Searched CRM for: '{query}'")
                return {"found": bool(res["clients"] or res["projects"] or res["tasks"]), "results": res}
            except Exception as e:
                return {"found": False, "error": str(e)}

        def save_current_plan(tasks: list, client_name: str = "", project_name: str = "") -> dict:
            if not chat_id:
                return {"success": False, "error": "No chat context."}
            try:
                chat = db.query(models.ChatConversation).filter(models.ChatConversation.id == chat_id).first()
                if chat:
                    chat.current_plan = json.dumps({"client_name": client_name, "project_name": project_name, "tasks": tasks}, indent=2)
                    db.add(models.Activity(action="PLAN_CREATED", entity_type="CHAT", entity_id=chat_id, description="AI generated an execution plan"))
                    db.commit()
                    actions_taken.append("Plan Saved to Memory")
                    return {"success": True, "message": "Plan saved."}
                return {"success": False, "error": "Chat not found."}
            except Exception as e:
                db.rollback()
                return {"success": False, "error": str(e)}

        def update_project_status(project_id: int = None, project_name: str = None, new_status: str = "COMPLETED") -> dict:
            if not is_explicit:
                return {"blocked": True, "reason": "Write action requires explicit user instruction."}
            project = None
            if project_id:
                project = db.query(models.Project).filter(models.Project.id == project_id).first()
            elif project_name:
                matches = [p for p in db.query(models.Project).all() if project_name.lower() in p.project_name.lower()]
                if len(matches) == 1:
                    project = matches[0]
                elif len(matches) > 1:
                    return {"success": False, "error": f"Multiple projects match '{project_name}'. Be more specific."}
                else:
                    return {"success": False, "error": f"No project found matching '{project_name}'."}
            if not project:
                return {"success": False, "error": "Project not found."}
            p_status = "COMPLETED" if new_status == "DONE" else new_status
            return self._execute_project_update(project, p_status, db, actions_taken)

        def update_task_status(task_id: int = None, task_title: str = None, new_status: str = "DONE") -> dict:
            if not is_explicit:
                return {"blocked": True, "reason": "Write action requires explicit user instruction."}
            task = None
            if task_id:
                task = db.query(models.Task).filter(models.Task.id == task_id).first()
            elif task_title:
                matches = [t for t in db.query(models.Task).all() if task_title.lower() in t.title.lower()]
                if len(matches) == 1:
                    task = matches[0]
                elif len(matches) > 1:
                    return {"success": False, "error": f"Multiple tasks match '{task_title}'. Be more specific."}
                else:
                    return {"success": False, "error": f"No task found matching '{task_title}'."}
            if not task:
                return {"success": False, "error": "Task not found."}
            return self._execute_task_update(task, new_status, db, actions_taken)

        tools_map = {
            "create_task": create_task,
            "get_task": get_task,
            "save_current_plan": save_current_plan,
            "search_crm": search_crm,
            "update_project_status": update_project_status,
            "update_task_status": update_task_status,
        }

        TOOLS_DEFINITION = [
            {
                "type": "function",
                "function": {
                    "name": "search_crm",
                    "description": "Search CRM for clients, projects, or tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string", "description": "Name or ID to search"}},
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_task",
                    "description": "Get a specific task by its ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {"task_id": {"type": "integer", "description": "The task ID number"}},
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task. Only use when user explicitly asks to create.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "priority": {"type": "string"},
                            "status": {"type": "string"},
                            "description": {"type": "string"},
                            "project_id": {"type": "integer"},
                            "client_id": {"type": "integer"},
                        },
                        "required": ["title", "priority", "status"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_project_status",
                    "description": "Update a project's status. Only use when user explicitly asks to update.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string"},
                            "project_id": {"type": "integer"},
                            "new_status": {"type": "string"},
                        },
                        "required": ["new_status"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task_status",
                    "description": "Update a task's status. Only use when user explicitly asks to update.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer"},
                            "task_title": {"type": "string"},
                            "new_status": {"type": "string"},
                        },
                        "required": ["new_status"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "save_current_plan",
                    "description": "Save an execution plan. Used for planning, NOT for creating tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "client_name": {"type": "string"},
                            "project_name": {"type": "string"},
                            "tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "status": {"type": "string"},
                                    },
                                },
                            },
                        },
                        "required": ["tasks"],
                    },
                },
            },
        ]

        # Build messages
        messages = [{"role": "system", "content": focused_system}]
        for h in history[-6:]:
            messages.append({
                "role": "user" if h["role"] == "user" else "assistant",
                "content": h.get("text", ""),
            })
        messages.append({"role": "user", "content": prompt})

        # Ollama call
        url = settings.OLLAMA_BASE_URL.rstrip('/') + "/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.3},
            "tools": TOOLS_DEFINITION,
        }

        final_text = ""
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}, method="POST",
            )
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
                        messages.append({"role": "tool", "content": json.dumps(tool_result, default=str)})

                    # Second call to get the final answer
                    payload["messages"] = messages
                    req2 = urllib.request.Request(
                        url, data=json.dumps(payload).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}, method="POST",
                    )
                    with urllib.request.urlopen(req2, timeout=300) as response2:
                        result2 = json.loads(response2.read().decode())
                        message2 = result2.get("message", {})
                        final_text = message2.get("content", "")
                        if not final_text or not str(final_text).strip():
                            final_text = "Request processed."
                else:
                    final_text = message.get("content", "")

                if chat_id:
                    db.add(models.Activity(
                        action="AI_REQUEST_OLLAMA", entity_type="CHAT",
                        entity_id=chat_id, description="Ollama request completed",
                    ))
                    db.commit()

        except urllib.error.URLError as e:
            err_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
            if 'timed out' in err_msg.lower() or 'timeout' in err_msg.lower():
                final_text = f"Ollama is running but the model took too long. ({err_msg})"
            elif 'connection refused' in err_msg.lower():
                final_text = "Ollama is offline. Please start Ollama and try again."
            else:
                final_text = f"Ollama connection error. ({err_msg})"
            if chat_id:
                db.add(models.Activity(action="AI_ERROR", entity_type="CHAT", entity_id=chat_id, description=final_text))
                db.commit()
        except TimeoutError as e:
            final_text = f"Model took too long to respond. ({e})"
            if chat_id:
                db.add(models.Activity(action="AI_ERROR", entity_type="CHAT", entity_id=chat_id, description=final_text))
                db.commit()
        except Exception as e:
            final_text = f"Ollama error: {e}"
            if chat_id:
                db.add(models.Activity(action="AI_ERROR", entity_type="CHAT", entity_id=chat_id, description=str(e)))
                db.commit()

        return {"text": final_text, "actions": actions_taken, "provider": "ollama", "model": settings.OLLAMA_MODEL}

    # ==================================================================
    # PRIVATE HELPERS
    # ==================================================================

    def _handle_update(self, entities, is_project, is_task, target_status, db, actions_taken) -> str:
        """
        Execute a server-side update.  Returns the response text on success,
        or None if the intent could not be resolved (fall through to Ollama).
        """

        # --- Explicit "project" keyword ---
        if is_project and not is_task:
            if not entities["projects"]:
                return "Koi matching project nahi mila database mein."
            if len(entities["projects"]) > 1:
                names = "\n".join(f"  - #{p.id} {p.project_name} ({p.status})" for p in entities["projects"])
                return f"Multiple projects found. Kaunsa update karna hai?\n\n{names}"
            p_status = "COMPLETED" if target_status == "DONE" else target_status
            result = self._execute_project_update(entities["projects"][0], p_status, db, actions_taken)
            return self._format_update_result(result, "project")

        # --- Explicit "task" keyword ---
        if is_task and not is_project:
            if not entities["tasks"]:
                return "Koi matching task nahi mila database mein."
            if len(entities["tasks"]) > 1:
                names = "\n".join(f"  - #{t.id} {t.title} ({t.status})" for t in entities["tasks"])
                return f"Multiple tasks found. Kaunsa update karna hai?\n\n{names}"
            result = self._execute_task_update(entities["tasks"][0], target_status, db, actions_taken)
            return self._format_update_result(result, "task")

        # --- Neither specified: infer from what was found ---
        if entities["projects"] and not entities["tasks"]:
            if len(entities["projects"]) == 1:
                p_status = "COMPLETED" if target_status == "DONE" else target_status
                result = self._execute_project_update(entities["projects"][0], p_status, db, actions_taken)
                return self._format_update_result(result, "project")

        if entities["tasks"] and not entities["projects"]:
            if len(entities["tasks"]) == 1:
                result = self._execute_task_update(entities["tasks"][0], target_status, db, actions_taken)
                return self._format_update_result(result, "task")

        # --- Both found: ask for clarification ---
        if entities["projects"] and entities["tasks"]:
            lines = []
            for p in entities["projects"]:
                lines.append(f"  Project: #{p.id} {p.project_name} ({p.status})")
            for t in entities["tasks"]:
                lines.append(f"  Task: #{t.id} {t.title} ({t.status})")
            return (
                "Project aur Task dono mile hain. Kaunsa update karna hai?\n\n"
                + "\n".join(lines)
                + "\n\nPlease specify: 'project status update karo' ya 'task status update karo'"
            )

        if not entities["projects"] and not entities["tasks"]:
            return "Koi matching project ya task nahi mila database mein."

        return None  # fall through to Ollama

    def _format_update_result(self, result: dict, entity_type: str) -> str:
        if not result.get("success"):
            return f"Update fail: {result.get('error', 'Unknown error')}"

        if result.get("already_done"):
            name = result.get("project_name") or result.get("title", "")
            status = result.get("status") or result.get("new_status", "")
            return f"'{name}' already {status} hai. Koi change nahi kiya."

        if entity_type == "project":
            text = (
                f"Done. Project '{result['project_name']}' ka status "
                f"{result['old_status']} se {result['new_status']} kar diya hai.\n"
                f"(Database verified)"
            )
            if result.get("progress") == 100:
                text += "\nProgress: 100%"
            return text

        # task
        text = (
            f"Done. Task #{result['task_id']} '{result['title']}' ka status "
            f"{result['old_status']} se {result['new_status']} kar diya hai.\n"
            f"(Database verified)"
        )
        if result.get("project_name") and result["project_name"] != "N/A":
            text += f"\nProject: {result['project_name']}"
        return text

    def _build_focused_system_prompt(self, crm_context: str) -> str:
        prompt = (
            "You are AIS AI Employee for Alag Innovative Solutions.\n"
            "Answer based ONLY on the CRM data provided below.\n"
            "Do NOT invent any client names, project names, task titles, statuses, or IDs.\n"
        )
        if crm_context:
            prompt += f"\n{crm_context}\n"
        else:
            prompt += "\nNo matching CRM records were found for this query.\n"

        prompt += (
            "\nRules:\n"
            "- Use ONLY the database records shown above. Never invent data.\n"
            "- If no matching record exists, say: 'Koi matching record nahi mila.'\n"
            "- For planning requests: create steps based on actual tasks above. Do NOT create DB records.\n"
            "- NEVER claim to have updated, created, or deleted anything unless a tool confirmed it.\n"
            "- Keep answers concise and factual.\n"
        )
        return prompt
