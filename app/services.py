from mysql.connector import Error
from .auth import hash_password_bcrypt_like, verify_password
from .management import (
    get_user_by_email,
    create_user,
    delete_user_by_email,
    list_users_by_role,
    assign_worker_to_recruiter,
    list_workers_for_recruiter,
    update_user_password,
    get_recruiter_for_worker,
    list_all_assignments,
    create_task,
    list_tasks_for_worker,
    update_task_status,
    check_in,
    check_out,
    today_status,
    start_global_session,
    stop_global_session,
    start_task_session,
    stop_task_session,
    global_today_summary,
    submit_eod,
    list_eod,
    list_eod_by_recruiter,
    task_time_summary,
)


def signup_recruiter(email: str, password: str):
    if get_user_by_email(email):
        return {"ok": False, "detail": "Email already exists"}
    user_id = create_user(email, hash_password_bcrypt_like(password), "recruiter")
    return {"ok": True, "id": user_id, "role": "recruiter"}

def remove_recruiter(email: str):
    user = get_user_by_email(email)
    if not user:
        return {"ok": False, "detail": "Recruiter not found"}
    if user.get("role") != "recruiter":
        return {"ok": False, "detail": f"Recruiter with email '{email}' not found or invalid role"}
    delete_user_by_email(email, role="recruiter")
    return {"ok": True, "detail": "Recruiter deleted successfully"}
def remove_worker(email: str):
    user = get_user_by_email(email)
    if not user:
        return {"ok": False, "detail": "Worker not found"}
    if user.get("role") not in ["hire", "worker"]:  # adjust depending on your schema
        return {"ok": False, "detail": f"Worker with email '{email}' not found or invalid role"}

    delete_user_by_email(email,role="hire")
    return {"ok": True, "detail": "Worker deleted successfully"}

def login_user(email: str, password: str):
    # Super admin override
    if email.lower() == "awais53562@gmail.com":
        if password == "Awais@123":
            return {"ok": True, "role": "admin", "email": email, "id": 0}
        return {"ok": False, "detail": "Invalid credentials"}

    user = get_user_by_email(email)
    if not user:
        return {"ok": False, "detail": "Invalid credentials"}
    if not verify_password(password, user["password_hashed"]):
        return {"ok": False, "detail": "Invalid credentials"}
    return {"ok": True, "role": user["role"], "email": user["email"], "id": user["id"]}


def get_recruiters():
    return {"ok": True, "items": list_users_by_role("recruiter")}


def get_workers():
    return {"ok": True, "items": list_users_by_role("hire")}


def create_worker(email: str, password: str):
    if get_user_by_email(email):
        return {"ok": False, "detail": "Email already exists"}
    user_id = create_user(email, hash_password_bcrypt_like(password), "hire")
    return {"ok": True, "id": user_id, "role": "hire"}



def change_password(email: str, old_password: str, new_password: str):
    user = get_user_by_email(email)
    if not user:
        return {"ok": False, "detail": "User not found"}

    # Verify old password
    if not verify_password(old_password, user["password_hashed"]):
        return {"ok": False, "detail": "Incorrect old password"}

    # Hash new password
    new_hashed = hash_password_bcrypt_like(new_password)

    # Update password in DB
    update_user_password(email, new_hashed)
    return {"ok": True, "detail": "Password updated successfully"}

def assign_worker(worker_id: int, recruiter_id: int):
    assign_worker_to_recruiter(worker_id, recruiter_id)
    return {"ok": True}


def recruiter_workers(recruiter_id: int):
    return {"ok": True, "items": list_workers_for_recruiter(recruiter_id)}


def worker_recruiter(worker_id: int):
    return {"ok": True, "item": get_recruiter_for_worker(worker_id)}


def all_assignments():
    return {"ok": True, "items": list_all_assignments()}


def add_task(recruiter_id: int, worker_id: int, title: str, description: str | None, priority: str, due_date: str | None):
    if priority not in ("low", "medium", "high"):
        priority = "medium"
    task_id = create_task(recruiter_id, worker_id, title, description, priority, due_date)
    return {"ok": True, "id": task_id}


def tasks_for_worker(worker_id: int):
    return {"ok": True, "items": list_tasks_for_worker(worker_id)}


def set_task_status(task_id: int, status: str):
    if status not in ("todo", "in_progress", "done"):
        return {"ok": False, "detail": "Invalid status"}
    update_task_status(task_id, status)
    return {"ok": True}


def worker_check_in(worker_id: int):
    check_in(worker_id)
    return {"ok": True}


def worker_check_out(worker_id: int):
    check_out(worker_id)
    return {"ok": True}


def worker_today(worker_id: int):
    return {"ok": True, "item": today_status(worker_id)}


def global_session_start(worker_id: int):
    start_global_session(worker_id)
    return {"ok": True}


def global_session_stop(worker_id: int):
    stop_global_session(worker_id)
    return {"ok": True}


def task_session_start(worker_id: int, task_id: int):
    start_task_session(worker_id, task_id)
    return {"ok": True}


def task_session_stop(worker_id: int, task_id: int, keystrokes: int, mouse_clicks: int, mouse_moves: int):
    stop_task_session(worker_id, task_id, keystrokes, mouse_clicks, mouse_moves)
    return {"ok": True}


def global_summary(worker_id: int):
    return {"ok": True, "item": global_today_summary(worker_id)}


def submit_end_of_day(worker_id: int, accomplishments: str, challenges: str, blockers: str, hours: int, next_day_plan: str):
    submit_eod(worker_id, accomplishments, challenges, blockers, hours, next_day_plan)
    return {"ok": True}


def get_eod(worker_id: int):
    return {"ok": True, "items": list_eod(worker_id)}


def get_eod_by_recruiter(recruiter_id: int):
    return {"ok": True, "items": list_eod_by_recruiter(recruiter_id)}


def get_detailed_time_analytics(worker_id: int, days: int = 30):
    """Get detailed time analytics for a worker"""
    from .management import get_detailed_time_analytics as mgmt_get_detailed_time_analytics
    return {"ok": True, "data": mgmt_get_detailed_time_analytics(worker_id, days)}


def get_task_time_summary(worker_id: int):
    return {"ok": True, "item": task_time_summary(worker_id)}


def create_support_ticket_service(worker_id: int, category: str, subject: str, description: str, priority: str = "medium", attendance_date: str = None):
    """Create a new support ticket"""
    from .management import create_support_ticket
    return create_support_ticket(worker_id, category, subject, description, priority, attendance_date)
def list_support_tickets_service():
    """List all support tickets for admin"""
    from .management import list_support_tickets
    return list_support_tickets()


def update_support_ticket_service(ticket_id: int, status: str = None, admin_response: str = None):
    """Update support ticket status and/or admin response"""
    from .management import update_support_ticket
    return update_support_ticket(ticket_id, status, admin_response)


def list_worker_support_tickets_service(worker_id: int):
    """List support tickets for a specific worker"""
    from .management import list_worker_support_tickets
    return list_worker_support_tickets(worker_id)


def add_conversation_message_service(ticket_id: int, sender_id: int, sender_role: str, message: str):
    """Add a message to the support ticket conversation"""
    from .management import add_conversation_message
    return add_conversation_message(ticket_id, sender_id, sender_role, message)


def get_conversation_messages_service(ticket_id: int):
    """Get all conversation messages for a support ticket"""
    from .management import get_conversation_messages
    return get_conversation_messages(ticket_id)


