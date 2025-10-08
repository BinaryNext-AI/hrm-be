import mysql.connector
from mysql.connector import Error
import os
from . import db


def ensure_users_table():
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hashed VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            conn.commit()


def get_user_by_email(email: str):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, email, password_hashed, role, created_at FROM users WHERE email=%s", (email,))
            return cur.fetchone()


def create_user(email: str, password_hashed: str, role: str):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hashed, role) VALUES (%s, %s, %s)",
                (email, password_hashed, role),
            )
            conn.commit()
            return cur.lastrowid


def list_users_by_role(role: str):
    # Use direct connection to avoid pool issues
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, email, role, created_at FROM users WHERE role=%s ORDER BY created_at DESC LIMIT 1000", (role,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error in list_users_by_role: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def assign_worker_to_recruiter(worker_id: int, recruiter_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "REPLACE INTO assignments (worker_id, recruiter_id) VALUES (%s, %s)",
                (worker_id, recruiter_id),
            )
            conn.commit()


def list_workers_for_recruiter(recruiter_id: int):
    # Use direct connection to avoid pool issues
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT u.id, u.email, u.role, u.created_at
                FROM assignments a
                JOIN users u ON u.id = a.worker_id
                WHERE a.recruiter_id = %s
                ORDER BY u.created_at DESC
                """,
                (recruiter_id,),
            )
            return cur.fetchall()
    except Exception as e:
        print(f"Error in list_workers_for_recruiter: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def get_recruiter_for_worker(worker_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT u.id, u.email, u.role, u.created_at
                FROM assignments a
                JOIN users u ON u.id = a.recruiter_id
                WHERE a.worker_id = %s
                """,
                (worker_id,),
            )
            return cur.fetchone()


def list_all_assignments():
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT a.id,
                       w.id AS worker_id, w.email AS worker_email,
                       r.id AS recruiter_id, r.email AS recruiter_email,
                       a.created_at
                FROM assignments a
                JOIN users w ON w.id = a.worker_id
                JOIN users r ON r.id = a.recruiter_id
                ORDER BY a.created_at DESC
                """
            )
            return cur.fetchall()


def create_task(recruiter_id: int, worker_id: int, title: str, description: str | None, priority: str, due_date: str | None):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (recruiter_id, worker_id, title, description, priority, due_date) VALUES (%s,%s,%s,%s,%s,%s)",
                (recruiter_id, worker_id, title, description, priority, due_date),
            )
            conn.commit()
            return cur.lastrowid


def list_tasks_for_worker(worker_id: int):
    # Use direct connection to avoid pool issues
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, recruiter_id, worker_id, title, description, priority, due_date, created_at, status FROM tasks WHERE worker_id=%s ORDER BY created_at DESC",
                (worker_id,),
            )
            return cur.fetchall()
    except Exception as e:
        print(f"Error in list_tasks_for_worker: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def update_task_status(task_id: int, status: str):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, task_id))
            conn.commit()


def check_in(worker_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO time_logs (worker_id, check_in, work_date) VALUES (%s, NOW(), CURDATE()) ON DUPLICATE KEY UPDATE check_in=IFNULL(check_in, NOW())",
                (worker_id,),
            )
            conn.commit()


def check_out(worker_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE time_logs SET check_out=NOW() WHERE worker_id=%s AND work_date=CURDATE()",
                (worker_id,),
            )
            conn.commit()


def today_status(worker_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT check_in, check_out FROM time_logs WHERE worker_id=%s AND work_date=CURDATE()",
                (worker_id,),
            )
            return cur.fetchone()


def start_global_session(worker_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO global_sessions (worker_id, start_at) VALUES (%s, NOW())",
                (worker_id,),
            )
            conn.commit()


def stop_global_session(worker_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE global_sessions SET end_at=NOW() WHERE worker_id=%s AND end_at IS NULL ORDER BY id DESC LIMIT 1",
                (worker_id,),
            )
            conn.commit()


def start_task_session(worker_id: int, task_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO task_sessions (worker_id, task_id, start_at) VALUES (%s, %s, NOW())",
                (worker_id, task_id),
            )
            conn.commit()


def stop_task_session(worker_id: int, task_id: int, keystrokes: int, mouse_clicks: int, mouse_moves: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE task_sessions
                SET end_at=NOW(), keystrokes=keystrokes+%s, mouse_clicks=mouse_clicks+%s, mouse_moves=mouse_moves+%s
                WHERE worker_id=%s AND task_id=%s AND end_at IS NULL
                ORDER BY id DESC LIMIT 1
                """,
                (keystrokes, mouse_clicks, mouse_moves, worker_id, task_id),
            )
            conn.commit()


def global_today_summary(worker_id: int):
    if db.pool is None:
        db.init_pool()
    with db.pool.get_conn() as conn:  # type: ignore[attr-defined]
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT SUM(TIMESTAMPDIFF(SECOND, start_at, COALESCE(end_at, NOW()))) AS elapsed
                FROM global_sessions
                WHERE worker_id=%s AND DATE(start_at)=CURDATE()
                """,
                (worker_id,),
            )
            row = cur.fetchone() or {"elapsed": 0}
            cur.execute(
                "SELECT start_at FROM global_sessions WHERE worker_id=%s AND end_at IS NULL ORDER BY id DESC LIMIT 1",
                (worker_id,),
            )
            open_row = cur.fetchone()
            active = open_row is not None
            return {"elapsed_seconds": int(row.get("elapsed") or 0), "active": active}


def submit_eod(worker_id: int, accomplishments: str, challenges: str, blockers: str, hours: int, next_day_plan: str):
    # Use direct connection to avoid pool issues
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor() as cur:
            # Get the recruiter_id for this worker
            cur.execute("SELECT recruiter_id FROM assignments WHERE worker_id = %s", (worker_id,))
            assignment = cur.fetchone()
            if not assignment:
                raise Exception("Worker not assigned to any recruiter")
            recruiter_id = assignment[0]
            
            cur.execute(
                """
                INSERT INTO end_of_day_reports (worker_id, recruiter_id, work_date, accomplishments, challenges, blockers, hours, next_day_plan)
                VALUES (%s, %s, CURDATE(), %s, %s, %s, %s, %s)
                """,
                (worker_id, recruiter_id, accomplishments, challenges, blockers, hours, next_day_plan),
            )
            conn.commit()
    except Exception as e:
        print(f"Error in submit_eod: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def list_eod(worker_id: int):
    # Use direct connection to avoid pool issues
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, work_date, hours, accomplishments, challenges, blockers, next_day_plan, submitted_at FROM end_of_day_reports WHERE worker_id=%s ORDER BY submitted_at DESC",
                (worker_id,),
            )
            return cur.fetchall()
    except Exception as e:
        print(f"Error in list_eod: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def list_eod_by_recruiter(recruiter_id: int):
    # Use direct connection to avoid pool issues - much more efficient!
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT eod.id, eod.worker_id, eod.recruiter_id, eod.work_date, eod.hours, 
                       eod.accomplishments, eod.challenges, eod.blockers, eod.next_day_plan, 
                       eod.submitted_at, u.email as worker_email
                FROM end_of_day_reports eod
                JOIN users u ON eod.worker_id = u.id
                WHERE eod.recruiter_id = %s 
                ORDER BY eod.submitted_at DESC
                """,
                (recruiter_id,),
            )
            return cur.fetchall()
    except Exception as e:
        print(f"Error in list_eod_by_recruiter: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def task_time_summary(worker_id: int):
    # Use direct connection to avoid pool issues
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT task_id,
                       SUM(TIMESTAMPDIFF(SECOND, start_at, COALESCE(end_at, NOW()))) AS seconds,
                       SUM(keystrokes) AS keystrokes,
                       SUM(mouse_clicks) AS mouse_clicks,
                       SUM(mouse_moves) AS mouse_moves
                FROM task_sessions
                WHERE worker_id=%s
                GROUP BY task_id
                """,
                (worker_id,),
            )
            rows = cur.fetchall()
            cur.execute(
                "SELECT SUM(TIMESTAMPDIFF(SECOND, start_at, COALESCE(end_at, NOW()))) AS seconds FROM global_sessions WHERE worker_id=%s",
                (worker_id,),
            )
            total = cur.fetchone() or {"seconds": 0}
            return {"per_task": rows, "total_seconds": int(total.get("seconds") or 0)}
    except Exception as e:
        print(f"Error in task_time_summary: {e}")
        return {"per_task": [], "total_seconds": 0}
    finally:
        if 'conn' in locals():
            conn.close()


def get_detailed_time_analytics(worker_id: int, days: int = 30):
    """Get detailed time analytics for a worker including daily breakdowns and session data"""
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='srv1919.hstgr.io',
            port=3306,
            user='u784288682_admin_hrm',
            password='Hammassir@123',
            database='u784288682_HRM_system',
            connection_timeout=10,
            autocommit=True
        )
        with conn.cursor(dictionary=True) as cur:
            # Daily global time breakdown
            cur.execute(
                """
                SELECT 
                    DATE(start_at) as work_date,
                    SUM(TIMESTAMPDIFF(SECOND, start_at, COALESCE(end_at, NOW()))) as total_seconds,
                    COUNT(*) as session_count,
                    CASE 
                        WHEN SUM(TIMESTAMPDIFF(SECOND, start_at, COALESCE(end_at, NOW()))) >= 28800 THEN 'completed'
                        WHEN SUM(TIMESTAMPDIFF(SECOND, start_at, COALESCE(end_at, NOW()))) >= 21600 THEN 'partial'
                        ELSE 'insufficient'
                    END as work_status
                FROM global_sessions 
                WHERE worker_id = %s 
                AND start_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(start_at)
                ORDER BY work_date DESC
                """,
                (worker_id, days),
            )
            daily_global = cur.fetchall()

            # Daily task time breakdown
            cur.execute(
                """
                SELECT 
                    DATE(start_at) as work_date,
                    SUM(TIMESTAMPDIFF(SECOND, start_at, COALESCE(end_at, NOW()))) as total_seconds,
                    COUNT(*) as session_count,
                    SUM(keystrokes) as total_keystrokes,
                    SUM(mouse_clicks) as total_mouse_clicks,
                    SUM(mouse_moves) as total_mouse_moves
                FROM task_sessions 
                WHERE worker_id = %s 
                AND start_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                AND end_at IS NOT NULL
                GROUP BY DATE(start_at)
                ORDER BY work_date DESC
                """,
                (worker_id, days),
            )
            daily_task = cur.fetchall()

            # Task-wise breakdown
            cur.execute(
                """
                SELECT 
                    t.id as task_id,
                    t.title as task_title,
                    t.status as task_status,
                    SUM(TIMESTAMPDIFF(SECOND, ts.start_at, COALESCE(ts.end_at, NOW()))) as total_seconds,
                    COUNT(ts.id) as session_count,
                    SUM(ts.keystrokes) as total_keystrokes,
                    SUM(ts.mouse_clicks) as total_mouse_clicks,
                    SUM(ts.mouse_moves) as total_mouse_moves
                FROM tasks t
                LEFT JOIN task_sessions ts ON t.id = ts.task_id
                WHERE t.worker_id = %s
                GROUP BY t.id, t.title, t.status
                ORDER BY total_seconds DESC
                """,
                (worker_id,),
            )
            task_breakdown = cur.fetchall()

            # Recent sessions (last 20)
            cur.execute(
                """
                SELECT 
                    ts.id,
                    ts.start_at,
                    ts.end_at,
                    TIMESTAMPDIFF(SECOND, ts.start_at, COALESCE(ts.end_at, NOW())) as duration_seconds,
                    ts.keystrokes,
                    ts.mouse_clicks,
                    ts.mouse_moves,
                    t.title as task_title
                FROM task_sessions ts
                LEFT JOIN tasks t ON ts.task_id = t.id
                WHERE ts.worker_id = %s
                ORDER BY ts.start_at DESC
                LIMIT 20
                """,
                (worker_id,),
            )
            recent_sessions = cur.fetchall()

            # Calculate work completion summary
            total_days = len(daily_global)
            completed_days = len([d for d in daily_global if d.get('work_status') == 'completed'])
            partial_days = len([d for d in daily_global if d.get('work_status') == 'partial'])
            insufficient_days = len([d for d in daily_global if d.get('work_status') == 'insufficient'])
            
            work_summary = {
                "total_days": total_days,
                "completed_days": completed_days,
                "partial_days": partial_days,
                "insufficient_days": insufficient_days,
                "completion_rate": round((completed_days / total_days * 100) if total_days > 0 else 0, 1),
                "target_hours": 8,
                "target_seconds": 28800
            }

            return {
                "daily_global": daily_global,
                "daily_task": daily_task,
                "task_breakdown": task_breakdown,
                "recent_sessions": recent_sessions,
                "work_summary": work_summary,
            }
    except Exception as e:
        print(f"Error in get_detailed_time_analytics: {e}")
        return {
            "daily_global": [],
            "daily_task": [],
            "task_breakdown": [],
            "recent_sessions": [],
        }
    finally:
        if 'conn' in locals():
            conn.close()


def create_support_ticket(worker_id: int, category: str, subject: str, description: str, priority: str = "medium"):
    """Create a new support ticket"""
    try:
        print(f"Creating support ticket: worker_id={worker_id}, category={category}, subject={subject}")
        if db.pool is None:
            db.init_pool()
        with db.pool.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO support_tickets (worker_id, category, subject, description, priority)
                    VALUES (%s, %s, %s, %s, %s)
                """, (worker_id, category, subject, description, priority))
                
                ticket_id = cur.lastrowid
                conn.commit()
                print(f"Support ticket created successfully with ID: {ticket_id}")
                return {"ok": True, "ticket_id": ticket_id}
    except Exception as e:
        print(f"Error creating support ticket: {e}")
        return {"ok": False, "message": str(e)}


def list_support_tickets():
    """List all support tickets for admin"""
    try:
        if db.pool is None:
            db.init_pool()
        with db.pool.get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT st.*, u.email as worker_email, u.role as worker_role
                    FROM support_tickets st
                    JOIN users u ON st.worker_id = u.id
                    ORDER BY st.created_at DESC
                """)
                
                tickets = cur.fetchall()
                return {"ok": True, "tickets": tickets}
    except Exception as e:
        print(f"Error listing support tickets: {e}")
        return {"ok": False, "message": str(e)}


def update_support_ticket(ticket_id: int, status: str = None, admin_response: str = None):
    """Update support ticket status and/or admin response"""
    try:
        print(f"Updating support ticket {ticket_id}: status={status}, admin_response={admin_response}")
        if db.pool is None:
            db.init_pool()
        with db.pool.get_conn() as conn:
            with conn.cursor() as cur:
                updates = []
                params = []
                
                if status:
                    updates.append("status = %s")
                    params.append(status)
                
                if admin_response:
                    updates.append("admin_response = %s")
                    params.append(admin_response)
                
                if updates:
                    params.append(ticket_id)
                    query = f"""
                        UPDATE support_tickets 
                        SET {', '.join(updates)}
                        WHERE id = %s
                    """
                    print(f"Executing query: {query}")
                    print(f"With params: {params}")
                    cur.execute(query, params)
                    conn.commit()
                    print(f"Successfully updated support ticket {ticket_id}")
                else:
                    print("No updates to perform")
                
                return {"ok": True}
    except Exception as e:
        print(f"Error updating support ticket: {e}")
        return {"ok": False, "message": str(e)}


def list_worker_support_tickets(worker_id: int):
    """List support tickets for a specific worker"""
    try:
        if db.pool is None:
            db.init_pool()
        with db.pool.get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT * FROM support_tickets 
                    WHERE worker_id = %s
                    ORDER BY created_at DESC
                """, (worker_id,))
                
                tickets = cur.fetchall()
                return {"ok": True, "tickets": tickets}
    except Exception as e:
        print(f"Error listing worker support tickets: {e}")
        return {"ok": False, "message": str(e)}


def add_conversation_message(ticket_id: int, sender_id: int, sender_role: str, message: str):
    """Add a message to the support ticket conversation"""
    try:
        print(f"Adding conversation message: ticket_id={ticket_id}, sender_id={sender_id}, sender_role={sender_role}")
        if db.pool is None:
            db.init_pool()
        with db.pool.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO support_conversations (ticket_id, sender_id, sender_role, message)
                    VALUES (%s, %s, %s, %s)
                """, (ticket_id, sender_id, sender_role, message))
                
                message_id = cur.lastrowid
                conn.commit()
                print(f"Conversation message added successfully with ID: {message_id}")
                return {"ok": True, "message_id": message_id}
    except Exception as e:
        print(f"Error adding conversation message: {e}")
        return {"ok": False, "message": str(e)}


def get_conversation_messages(ticket_id: int):
    """Get all conversation messages for a support ticket"""
    try:
        if db.pool is None:
            db.init_pool()
        with db.pool.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT sc.id, sc.sender_id, sc.sender_role, sc.message, sc.created_at, u.email
                    FROM support_conversations sc
                    JOIN users u ON sc.sender_id = u.id
                    WHERE sc.ticket_id = %s 
                    ORDER BY sc.created_at ASC
                """, (ticket_id,))
                
                messages = []
                for row in cur.fetchall():
                    messages.append({
                        "id": row[0],
                        "sender_id": row[1],
                        "sender_role": row[2],
                        "message": row[3],
                        "created_at": row[4].isoformat() if row[4] else None,
                        "sender_email": row[5],
                    })
                
                return {"ok": True, "messages": messages}
    except Exception as e:
        print(f"Error getting conversation messages: {e}")
        return {"ok": False, "message": str(e)}


