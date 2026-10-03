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
    # DATE PARSING & ENTITY EXTRACTION
    # ==================================================================

    def _parse_date(self, text: str):
        """Parse DD/MM/YYYY or YYYY-MM-DD from text into (datetime, DD/MM/YYYY string)."""
        # Match DD/MM/YYYY or DD-MM-YYYY
        m = re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', text)
        if m:
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                dt = datetime(year, month, day)
                return dt, f"{day:02d}/{month:02d}/{year}"
            except ValueError:
                pass
        # Match YYYY-MM-DD or YYYY/MM/DD
        m = re.search(r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b', text)
        if m:
            year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                dt = datetime(year, month, day)
                return dt, f"{day:02d}/{month:02d}/{year}"
            except ValueError:
                pass
        return None, None

    def _clean_entity_name(self, name: str) -> str:
        """Strip filler words, action phrases, and punctuation from an extracted entity name."""
        if not name:
            return ""
        name = re.sub(r'^(client|project)\s*[:=]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[\s\-]*(?:aur\s+)?deadline\s*[:=]?\s*[\d/\-]+.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[\s\-]+add\s+these.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[\s\-]+add\b.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(?:banana\s+hai|banani\s+hai|banwana\s+hai|banao|bana\s+do|kar\s+do|karo|bana)\b.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+project\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+client\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(?:with|ki|ke|ka)\s*$', '', name, flags=re.IGNORECASE)
        return name.strip(' ,;:-"\'')

    def _extract_client_and_project(self, prompt: str):
        """Extract (client_name, project_name, deadline_dt, deadline_str) from natural language prompt."""
        t = prompt.strip()
        date_dt, date_str = self._parse_date(t)

        # 1. Key-value: Client: X, Project: Y
        m = re.search(r'client\s*[:=]\s*([^,;]+?)\s*[,;]?\s*project\s*[:=]\s*([^,;]+)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 2. Key-value: Project: Y, Client: X
        m = re.search(r'project\s*[:=]\s*([^,;]+?)\s*[,;]?\s*client\s*[:=]\s*([^,;]+)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(2)), self._clean_entity_name(m.group(1)), date_dt, date_str

        # 3. English: add/create client X and/with project Y
        m = re.search(r'(?:add|create)\s+client\s+(.+?)\s+(?:and|with|,)\s+project\s+(.+)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 4. English: project Y add/create for client X
        m = re.search(r'(.+?)\s+project\s+(?:add\s+karo|add|create)\s+(?:for\s+client|for)\s+(.+)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(2)), self._clean_entity_name(m.group(1)), date_dt, date_str

        # 5. Hinglish Pattern 1: "<client> name/naam ke client ka/ki/ke <project> ..."
        m = re.search(r'([\w\s]+?)\s+(?:name|naam)\s+ke\s+client\s+(?:ka|ki|ke)\s+(.+)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 6. Hinglish Pattern 2: "<client> client add karo aur <project> project banao"
        m = re.search(r'([\w\s]+?)\s+client\s+(?:add\s+karo|add)\s+(?:aur|and|,)\s+(.+?)\s+project\s+(?:banao|bana\s+do|add\s+karo|add|create)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 7. Hinglish Pattern 3: "<client> ke liye <project> project (add karo|banao)"
        m = re.search(r'([\w\s]+?)\s+ke\s+liye\s+(.+?)\s+project\s+(?:add\s+karo|banao|bana\s+do|add|create)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 8. Hinglish Pattern 4: "<client> ke/ka/ki <project> project ki deadline"
        m = re.search(r'([\w\s]+?)\s+(?:ke|ka|ki)\s+(.+?)\s+project\s+ki\s+deadline', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 9. Hinglish Pattern 5: "<client> ke/ka/ki <project> project ka status"
        m = re.search(r'([\w\s]+?)\s+(?:ke|ka|ki)\s+(.+?)\s+project\s+ka\s+status', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 10. Hinglish Pattern 6: "<client> ka/ki/ke <project> banana hai"
        m = re.search(r'([\w\s]+?)\s+(?:ka|ki|ke)\s+(.+?)\s+(?:banana\s+hai|banani\s+hai|banwana\s+hai)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), self._clean_entity_name(m.group(2)), date_dt, date_str

        # 11. "<client> client add karo"
        m = re.search(r'([\w\s]+?)\s+client\s+(?:add\s+karo|add|create\s+karo|create)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), None, date_dt, date_str

        # 12. "add client <client>"
        m = re.search(r'(?:add|create)\s+client\s+([\w\s]+)', t, re.IGNORECASE)
        if m:
            return self._clean_entity_name(m.group(1)), None, date_dt, date_str

        return None, None, date_dt, date_str

    # ==================================================================
    # INTENT DETECTION
    # ==================================================================

    _CREATE_KEYWORDS = [
        "banana hai", "banani hai", "banwana hai", "banao", "bana do", "banaye",
        "add these", "add karo", "add kar do",
        "create karo", "create kar do", "create",
        "insert karo", "insert",
        "naya client", "new client", "naya project", "new project",
        "client add", "project add",
        "add client", "add project",
        "create client", "create project",
    ]

    _DEADLINE_KEYWORDS = ["deadline", "due date", "tarikh", "tareekh"]

    def _is_explicit_action(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        planning_words = ["plan", "suggest", "recommend", "how to", "break down", "list"]
        action_overrides = ["ab create", "save karo", "execute", "create task", "update", "mark", "change status", "add these", "banana hai", "banao"]
        if any(w in prompt_lower for w in planning_words) and not any(a in prompt_lower for a in action_overrides):
            return False

        action_words = [
            "create", "add", "insert", "save", "update", "execute",
            "do it", "karo", "kar do", "bana do", "banao", "banana hai",
            "mark", "change status", "complete karo", "completed karo",
            "done karo", "done mark", "completed mark", "add these",
        ]
        return any(w in prompt_lower for w in action_words)

    def _is_create_intent(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        return any(k in prompt_lower for k in self._CREATE_KEYWORDS)

    def _is_deadline_update_intent(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        has_deadline = any(k in prompt_lower for k in self._DEADLINE_KEYWORDS)
        dt, _ = self._parse_date(prompt)
        has_action = any(k in prompt_lower for k in ["kar do", "kardo", "karo", "update", "set", "change", "badal", "karna hai"])
        is_create = self._is_create_intent(prompt)
        return has_deadline and (dt is not None) and has_action and not is_create

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
    # ENTITY RESOLUTION FOR READ / SEARCH
    # ==================================================================

    _NOISE_WORDS = {
        "update", "status", "completed", "complete", "done", "mark",
        "karo", "kar", "do", "kya", "hai", "ka", "ke", "ki", "ko",
        "project", "task", "batao", "dikhao", "details", "change",
        "set", "to", "the", "is", "and", "for", "me", "mein",
        "planning", "progress", "backlog", "cancelled", "pending",
        "in_progress", "todo", "banana", "banao", "add", "these",
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
                deadline_str = p.deadline.strftime('%d/%m/%Y') if p.deadline else "Not set"
                parts.append(
                    f"Project #{p.id}: {p.project_name} | Client: {client_name} "
                    f"| Status: {p.status} | Progress: {p.progress}% | Priority: {p.priority} | Deadline: {deadline_str}"
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
    # DATABASE WRITE ACTIONS WITH READ-BACK VERIFICATION
    # ==================================================================

    def _execute_find_or_create_client_project(
        self, client_name: str, project_name: str, deadline_dt: datetime,
        deadline_str: str, db, actions_taken: list
    ) -> dict:
        """
        Create or find client and project with duplicate prevention,
        commit, and read-back verification.
        """
        try:
            client = None
            client_created = False

            # --- 1. Client Find or Create ---
            if client_name:
                norm_client = client_name.strip().lower()
                all_clients = db.query(models.Client).all()
                client = next((c for c in all_clients if c.business_name.strip().lower() == norm_client), None)

                if not client:
                    client = models.Client(business_name=client_name.strip(), status="ACTIVE")
                    db.add(client)
                    db.commit()
                    db.refresh(client)
                    client_created = True

                    # Verify client created
                    verified_c = db.query(models.Client).filter(models.Client.id == client.id).first()
                    if not verified_c:
                        return {"success": False, "error": f"Client '{client_name}' database verification failed."}

                    db.add(models.Activity(
                        action="CLIENT_CREATED", entity_type="CLIENT", entity_id=client.id,
                        description=f"Client '{client.business_name}' created"
                    ))
                    db.commit()
                    actions_taken.append(f"Created client #{client.id} '{client.business_name}'")
                else:
                    actions_taken.append(f"Found existing client #{client.id} '{client.business_name}'")

            # --- 2. Project Find or Create ---
            project = None
            project_created = False
            project_updated = False

            if project_name:
                # Format project name to title case
                formatted_proj_name = " ".join(w.capitalize() for w in project_name.strip().split())
                norm_proj = formatted_proj_name.lower()

                # Search existing project for this client
                existing_project = None
                if client:
                    for p in db.query(models.Project).filter(models.Project.client_id == client.id).all():
                        if p.project_name.strip().lower() == norm_proj:
                            existing_project = p
                            break

                # If not found for client, check unassigned project
                if not existing_project:
                    for p in db.query(models.Project).all():
                        if p.project_name.strip().lower() == norm_proj and (p.client_id is None or (client and p.client_id == client.id)):
                            if client and not p.client_id:
                                p.client_id = client.id
                            existing_project = p
                            break

                if existing_project:
                    project = existing_project
                    if deadline_dt and project.deadline != deadline_dt:
                        project.deadline = deadline_dt
                        project_updated = True
                        db.commit()
                        db.refresh(project)
                        actions_taken.append(f"Updated deadline of Project #{project.id} '{project.project_name}' to {deadline_str}")
                    else:
                        actions_taken.append(f"Reused existing Project #{project.id} '{project.project_name}'")
                else:
                    project = models.Project(
                        project_name=formatted_proj_name,
                        client_id=client.id if client else None,
                        deadline=deadline_dt,
                        status="PLANNING",
                        progress=0,
                        priority="MEDIUM"
                    )
                    db.add(project)
                    db.commit()
                    db.refresh(project)
                    project_created = True

                    # Verify project created
                    verified_p = db.query(models.Project).filter(models.Project.id == project.id).first()
                    if not verified_p:
                        return {"success": False, "error": f"Project '{formatted_proj_name}' database verification failed."}
                    if client and verified_p.client_id != client.id:
                        return {"success": False, "error": "Project client association verification failed."}
                    if deadline_dt and verified_p.deadline != deadline_dt:
                        return {"success": False, "error": "Project deadline verification failed."}

                    actions_taken.append(f"Created project #{project.id} '{project.project_name}' with deadline {deadline_str or 'None'}")

                # Update client's project count
                if client:
                    client.project_count = db.query(models.Project).filter(models.Project.client_id == client.id).count()
                    db.commit()

                # Activity logging
                if project_created:
                    c_name = client.business_name if client else "N/A"
                    db.add(models.Activity(
                        action="PROJECT_CREATED", entity_type="PROJECT", entity_id=project.id,
                        description=f"Project '{project.project_name}' created for client '{c_name}' with deadline {deadline_str or 'None'}"
                    ))
                    db.commit()
                elif project_updated:
                    db.add(models.Activity(
                        action="PROJECT_UPDATED", entity_type="PROJECT", entity_id=project.id,
                        description=f"Project '{project.project_name}' deadline updated to {deadline_str}"
                    ))
                    db.commit()

            return {
                "success": True,
                "verified": True,
                "client": client,
                "project": project,
                "client_created": client_created,
                "project_created": project_created,
                "project_updated": project_updated,
                "deadline_str": deadline_str
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

    def _execute_deadline_update(
        self, client_name: str, project_name: str, deadline_dt: datetime,
        deadline_str: str, db, actions_taken: list
    ) -> dict:
        """Update deadline of an existing project with verification."""
        try:
            project = None
            if project_name:
                norm_proj = project_name.strip().lower()
                candidates = [p for p in db.query(models.Project).all() if norm_proj in p.project_name.lower()]
                if client_name and len(candidates) > 1:
                    norm_client = client_name.strip().lower()
                    client_candidates = [p for p in candidates if p.client and norm_client in p.client.business_name.lower()]
                    if client_candidates:
                        candidates = client_candidates
                if candidates:
                    project = candidates[0]

            if not project and client_name:
                norm_client = client_name.strip().lower()
                for c in db.query(models.Client).all():
                    if norm_client in c.business_name.lower():
                        client_projs = db.query(models.Project).filter(models.Project.client_id == c.id).all()
                        if len(client_projs) == 1:
                            project = client_projs[0]
                            break

            if not project:
                return {"success": False, "error": f"Project '{project_name or ''}' database mein nahi mila."}

            old_deadline_str = project.deadline.strftime('%d/%m/%Y') if project.deadline else "Not set"
            project.deadline = deadline_dt
            db.commit()

            # Read-back verification
            db.refresh(project)
            if project.deadline != deadline_dt:
                return {"success": False, "verified": False, "error": "Database deadline verification failed."}

            db.add(models.Activity(
                action="PROJECT_UPDATED",
                entity_type="PROJECT",
                entity_id=project.id,
                description=f"Project '{project.project_name}' deadline updated: {old_deadline_str} -> {deadline_str}"
            ))
            db.commit()

            actions_taken.append(f"Updated deadline of Project #{project.id} '{project.project_name}' to {deadline_str}")
            return {
                "success": True,
                "verified": True,
                "project": project,
                "old_deadline_str": old_deadline_str,
                "deadline_str": deadline_str
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

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
    # RESPONSE FORMATTERS
    # ==================================================================

    def _format_create_result(self, result: dict) -> str:
        if not result.get("success"):
            return f"Action failed: {result.get('error', 'Unknown error')}"

        client = result.get("client")
        project = result.get("project")
        c_created = result.get("client_created", False)
        p_created = result.get("project_created", False)
        p_updated = result.get("project_updated", False)
        dl_str = result.get("deadline_str")

        c_name = client.business_name if client else "N/A"
        c_id = client.id if client else "N/A"
        p_name = project.project_name if project else "N/A"
        p_id = project.id if project else "N/A"
        p_status = project.status if project else "PLANNING"
        final_dl = dl_str or (project.deadline.strftime('%d/%m/%Y') if (project and project.deadline) else 'Not set')

        # Format concise output matching Requirement 7
        if c_created and p_created:
            text = (
                f"Done. Client '{c_name}' added successfully and '{p_name}' project created"
                f"{f' with deadline {dl_str}' if dl_str else ''}.\n"
                f"(Database verified)\n\n"
                f"• Client: {c_name} (ID: #{c_id})\n"
                f"• Project: {p_name} (ID: #{p_id})\n"
                f"• Status: {p_status}\n"
                f"• Deadline: {final_dl}"
            )
        elif not c_created and p_created:
            text = (
                f"Done. Existing client '{c_name}' used and '{p_name}' project created"
                f"{f' with deadline {dl_str}' if dl_str else ''}.\n"
                f"(Database verified)\n\n"
                f"• Client: {c_name} (ID: #{c_id})\n"
                f"• Project: {p_name} (ID: #{p_id})\n"
                f"• Status: {p_status}\n"
                f"• Deadline: {final_dl}"
            )
        elif p_updated:
            text = (
                f"Done. Client '{c_name}' used and existing project '{p_name}' updated"
                f"{f' with deadline {dl_str}' if dl_str else ''}.\n"
                f"(Database verified)\n\n"
                f"• Client: {c_name} (ID: #{c_id})\n"
                f"• Project: {p_name} (ID: #{p_id})\n"
                f"• Status: {p_status}\n"
                f"• Deadline: {final_dl}"
            )
        else:
            # Reused with no changes (TEST B)
            text = (
                f"Done. Existing client '{c_name}' used and existing project '{p_name}' reused"
                f"{f' with deadline {dl_str}' if dl_str else ''}.\n"
                f"(Database verified - no duplicate created)\n\n"
                f"• Client: {c_name} (ID: #{c_id})\n"
                f"• Project: {p_name} (ID: #{p_id})\n"
                f"• Status: {p_status}\n"
                f"• Deadline: {final_dl}"
            )
        return text

    def _format_deadline_result(self, result: dict) -> str:
        if not result.get("success"):
            return f"Deadline update failed: {result.get('error', 'Unknown error')}"
        p = result["project"]
        c_name = p.client.business_name if p.client else "N/A"
        return (
            f"Done. Project '{p.project_name}' ki deadline {result['deadline_str']} update kar di hai.\n"
            f"(Database verified)\n\n"
            f"• Project: {p.project_name} (ID: #{p.id})\n"
            f"• Client: {c_name}\n"
            f"• Previous Deadline: {result['old_deadline_str']}\n"
            f"• New Deadline: {result['deadline_str']}"
        )

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

    def _handle_update(self, entities, is_project, is_task, target_status, db, actions_taken) -> str:
        """Execute a server-side status update."""
        if is_project and not is_task:
            if not entities["projects"]:
                return "Koi matching project nahi mila database mein."
            if len(entities["projects"]) > 1:
                # If a client was also matched, prioritize project of that client
                if entities["clients"]:
                    c_ids = {c.id for c in entities["clients"]}
                    c_projs = [p for p in entities["projects"] if p.client_id in c_ids]
                    if len(c_projs) == 1:
                        p_status = "COMPLETED" if target_status == "DONE" else target_status
                        result = self._execute_project_update(c_projs[0], p_status, db, actions_taken)
                        return self._format_update_result(result, "project")

                names = "\n".join(f"  - #{p.id} {p.project_name} ({p.status})" for p in entities["projects"])
                return f"Multiple projects found. Kaunsa update karna hai?\n\n{names}"

            p_status = "COMPLETED" if target_status == "DONE" else target_status
            result = self._execute_project_update(entities["projects"][0], p_status, db, actions_taken)
            return self._format_update_result(result, "project")

        if is_task and not is_project:
            if not entities["tasks"]:
                return "Koi matching task nahi mila database mein."
            if len(entities["tasks"]) > 1:
                names = "\n".join(f"  - #{t.id} {t.title} ({t.status})" for t in entities["tasks"])
                return f"Multiple tasks found. Kaunsa update karna hai?\n\n{names}"
            result = self._execute_task_update(entities["tasks"][0], target_status, db, actions_taken)
            return self._format_update_result(result, "task")

        if entities["projects"] and not entities["tasks"]:
            if len(entities["projects"]) == 1:
                p_status = "COMPLETED" if target_status == "DONE" else target_status
                result = self._execute_project_update(entities["projects"][0], p_status, db, actions_taken)
                return self._format_update_result(result, "project")

        if entities["tasks"] and not entities["projects"]:
            if len(entities["tasks"]) == 1:
                result = self._execute_task_update(entities["tasks"][0], target_status, db, actions_taken)
                return self._format_update_result(result, "task")

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

        return None

    # ==================================================================
    # MAIN RESPONSE GENERATOR
    # ==================================================================

    def generate_response(self, prompt: str, system_context: str, history: list, db, chat_id: int = None) -> dict:
        settings.reload()

        actions_taken = []
        is_explicit = self._is_explicit_action(prompt)

        # ==============================================================
        # PHASE 1: SERVER-SIDE DETERMINISTIC ACTION EXECUTION
        # Handles CREATE and UPDATE actions BEFORE calling Ollama.
        # This guarantees:
        # 1. Guaranteed database write + commit
        # 2. Read-back verification
        # 3. LLM physically cannot fabricate success or return "not found"
        # ==============================================================

        # --- ACTION A: DEADLINE UPDATE ---
        if is_explicit and self._is_deadline_update_intent(prompt):
            extracted_c, extracted_p, deadline_dt, deadline_str = self._extract_client_and_project(prompt)
            if deadline_dt:
                res = self._execute_deadline_update(extracted_c, extracted_p, deadline_dt, deadline_str, db, actions_taken)
                return {
                    "text": self._format_deadline_result(res),
                    "actions": actions_taken,
                    "provider": "ollama",
                    "model": settings.OLLAMA_MODEL
                }

        # --- ACTION B: STATUS UPDATE ---
        if is_explicit and self._is_update_intent(prompt):
            target_status = self._detect_target_status(prompt)
            if target_status:
                extracted_c, extracted_p, _, _ = self._extract_client_and_project(prompt)
                # If specific project was extracted, try finding it directly
                if extracted_p:
                    candidates = [p for p in db.query(models.Project).all() if extracted_p.lower() in p.project_name.lower()]
                    if extracted_c and len(candidates) > 1:
                        client_candidates = [p for p in candidates if p.client and extracted_c.lower() in p.client.business_name.lower()]
                        if client_candidates:
                            candidates = client_candidates
                    if len(candidates) == 1:
                        p_status = "COMPLETED" if target_status == "DONE" else target_status
                        result = self._execute_project_update(candidates[0], p_status, db, actions_taken)
                        return {
                            "text": self._format_update_result(result, "project"),
                            "actions": actions_taken,
                            "provider": "ollama",
                            "model": settings.OLLAMA_MODEL
                        }

                entities = self._find_matching_entities(prompt, db)
                is_project, is_task = self._is_project_or_task(prompt)
                result_text = self._handle_update(entities, is_project, is_task, target_status, db, actions_taken)
                if result_text is not None:
                    return {
                        "text": result_text,
                        "actions": actions_taken,
                        "provider": "ollama",
                        "model": settings.OLLAMA_MODEL
                    }

        # --- ACTION C: CREATE / ADD CLIENT & PROJECT ---
        if is_explicit and self._is_create_intent(prompt):
            extracted_c, extracted_p, deadline_dt, deadline_str = self._extract_client_and_project(prompt)
            if extracted_c or extracted_p:
                create_res = self._execute_find_or_create_client_project(
                    extracted_c, extracted_p, deadline_dt, deadline_str, db, actions_taken
                )
                return {
                    "text": self._format_create_result(create_res),
                    "actions": actions_taken,
                    "provider": "ollama",
                    "model": settings.OLLAMA_MODEL
                }

        # ==============================================================
        # PHASE 2: CRM PRE-FETCH (READ QUERIES & CONVERSATION)
        # ==============================================================

        entities = self._find_matching_entities(prompt, db)
        crm_context = self._format_crm_context(entities, db)

        if crm_context:
            actions_taken.append(
                f"CRM lookup: {len(entities['clients'])} clients, "
                f"{len(entities['projects'])} projects, {len(entities['tasks'])} tasks"
            )

        # ==============================================================
        # PHASE 3: BUILD FOCUSED PROMPT + CALL OLLAMA WITH TOOLS
        # ==============================================================

        focused_system = self._build_focused_system_prompt(crm_context)

        # Tool functions for Ollama fallback
        def create_client(business_name: str) -> dict:
            return self._execute_find_or_create_client_project(business_name, None, None, None, db, actions_taken)

        def create_project(project_name: str, client_name: str = None, deadline: str = None) -> dict:
            dt, ds = self._parse_date(deadline) if deadline else (None, None)
            return self._execute_find_or_create_client_project(client_name, project_name, dt, ds, db, actions_taken)

        def update_project_deadline(project_name: str, deadline: str) -> dict:
            dt, ds = self._parse_date(deadline) if deadline else (None, None)
            return self._execute_deadline_update(None, project_name, dt, ds, db, actions_taken)

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
            "create_client": create_client,
            "create_project": create_project,
            "update_project_deadline": update_project_deadline,
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
                    "name": "create_client",
                    "description": "Create a new client in the database.",
                    "parameters": {
                        "type": "object",
                        "properties": {"business_name": {"type": "string"}},
                        "required": ["business_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_project",
                    "description": "Create a new project associated with a client in the database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string"},
                            "client_name": {"type": "string"},
                            "deadline": {"type": "string", "description": "DD/MM/YYYY date format"}
                        },
                        "required": ["project_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_project_deadline",
                    "description": "Update deadline for a project.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string"},
                            "deadline": {"type": "string", "description": "DD/MM/YYYY date format"}
                        },
                        "required": ["project_name", "deadline"],
                    },
                },
            },
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
