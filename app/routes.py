from fastapi import APIRouter, Query, Form
from .services import (
    signup_recruiter,
    login_user,
    get_recruiters,
    get_workers,
    create_worker,
    assign_worker,
    recruiter_workers,
    worker_recruiter,
    all_assignments,
    add_task,
    tasks_for_worker,
    set_task_status,
    worker_check_in,
    worker_check_out,
    worker_today,
    global_session_start,
    global_session_stop,
    task_session_start,
    task_session_stop,
    global_summary,
    submit_end_of_day,
    get_eod,
    get_eod_by_recruiter,
    get_task_time_summary,
    get_detailed_time_analytics,
    create_support_ticket_service,
    list_support_tickets_service,
    update_support_ticket_service,
    list_worker_support_tickets_service,
    add_conversation_message_service,
    get_conversation_messages_service,
)


router = APIRouter()


@router.get("/ping")
def ping():
    return {"ok": True}


@router.post("/auth/signup")
def signup(email: str, password: str):
    return signup_recruiter(email, password)


@router.post("/auth/login")
def login(email: str, password: str):
    return login_user(email, password)


@router.post("/auth/logout")
def logout():
    # Stateless logout: frontend should clear stored tokens/session
    return {"ok": True}


@router.get("/admin/recruiters")
def list_recruiters():
    return get_recruiters()


@router.get("/admin/workers")
def list_workers():
    return get_workers()


@router.post("/admin/workers")
def add_worker(email: str, password: str):
    return create_worker(email, password)


@router.post("/admin/assign")
def assign(worker_id: int, recruiter_id: int):
    return assign_worker(worker_id, recruiter_id)


@router.get("/recruiter/workers")
def get_my_workers(recruiter_id: int):
    return recruiter_workers(recruiter_id)


@router.get("/worker/recruiter")
def get_my_recruiter(worker_id: int):
    return worker_recruiter(worker_id)


@router.get("/admin/assignments")
def list_assignments():
    return all_assignments()


@router.post("/tasks")
def create_task_endpoint(recruiter_id: int, worker_id: int, title: str, description: str | None = None, priority: str = "medium", due_date: str | None = None):
    return add_task(recruiter_id, worker_id, title, description, priority, due_date)


@router.get("/tasks")
def list_tasks(worker_id: int):
    return tasks_for_worker(worker_id)


@router.post("/tasks/status")
def update_task_status_endpoint(task_id: int, status: str):
    return set_task_status(task_id, status)


@router.post("/time/check-in")
def time_check_in(worker_id: int):
    return worker_check_in(worker_id)


@router.post("/time/check-out")
def time_check_out(worker_id: int):
    return worker_check_out(worker_id)


@router.get("/time/today")
def time_today(worker_id: int):
    return worker_today(worker_id)


@router.post("/time/global/start")
def api_global_start(worker_id: int):
    return global_session_start(worker_id)


@router.post("/time/global/stop")
def api_global_stop(worker_id: int):
    return global_session_stop(worker_id)


@router.post("/time/task/start")
def api_task_start(worker_id: int, task_id: int):
    return task_session_start(worker_id, task_id)


@router.post("/time/task/stop")
def api_task_stop(worker_id: int, task_id: int, keystrokes: int = 0, mouse_clicks: int = 0, mouse_moves: int = 0):
    return task_session_stop(worker_id, task_id, keystrokes, mouse_clicks, mouse_moves)


@router.get("/time/global/summary")
def api_global_summary(worker_id: int):
    return global_summary(worker_id)


@router.post("/reports/eod")
def api_submit_eod(worker_id: int, accomplishments: str, challenges: str = "", blockers: str = "", hours: int = 0, next_day_plan: str = ""):
    return submit_end_of_day(worker_id, accomplishments, challenges, blockers, hours, next_day_plan)


@router.get("/reports/eod")
def api_get_eod(worker_id: int):
    return get_eod(worker_id)


@router.get("/reports/eod/recruiter")
def api_get_eod_by_recruiter(recruiter_id: int):
    return get_eod_by_recruiter(recruiter_id)


@router.get("/analytics/time/detailed")
def api_get_detailed_time_analytics(worker_id: int, days: int = 30):
    return get_detailed_time_analytics(worker_id, days)


@router.get("/time/task/summary")
def api_task_time_summary(worker_id: int):
    return get_task_time_summary(worker_id)


# Support Tickets
@router.post("/support/tickets")
def api_create_support_ticket(worker_id: int, category: str, subject: str, description: str, priority: str = "medium"):
    return create_support_ticket_service(worker_id, category, subject, description, priority)


@router.get("/admin/support/tickets")
def api_list_support_tickets():
    return list_support_tickets_service()


@router.put("/admin/support/tickets/{ticket_id}")
def api_update_support_ticket(ticket_id: int, status: str = Form(None), admin_response: str = Form(None)):
    return update_support_ticket_service(ticket_id, status, admin_response)


@router.get("/support/tickets/worker")
def api_list_worker_support_tickets(worker_id: int):
    return list_worker_support_tickets_service(worker_id)


@router.post("/support/conversations")
def api_add_conversation_message(ticket_id: int = Form(...), sender_id: int = Form(...), sender_role: str = Form(...), message: str = Form(...)):
    return add_conversation_message_service(ticket_id, sender_id, sender_role, message)


@router.get("/support/conversations/{ticket_id}")
def api_get_conversation_messages(ticket_id: int):
    return get_conversation_messages_service(ticket_id)


