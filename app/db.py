from typing import Optional
import os
from urllib.parse import quote_plus

import mysql.connector
from mysql.connector import pooling, Error


def build_dsn_from_env() -> dict:
    # Hardcoded credentials per user request
    return {
        "host": "srv1919.hstgr.io",
        "port": 3306,
        "user": "u784288682_admin_hrm",
        "password": "Hammassir@123",
        "database": "u784288682_HRM_system",
        "connection_timeout": 10,
        "autocommit": True,
        "charset": "utf8mb4",
        "use_unicode": True,
    }


class MySQLPool:
    def __init__(self, pool_name: str = "hrm_pool", pool_size: int = 5):
        cfg = build_dsn_from_env()
        # Add pool-specific settings
        pool_cfg = {
            **cfg,
            "pool_name": pool_name,
            "pool_size": pool_size,
            "pool_reset_session": True,
            "autocommit": True,
        }
        self.pool = pooling.MySQLConnectionPool(**pool_cfg)

    def get_conn(self):
        return self.pool.get_connection()


pool: Optional[MySQLPool] = None


def init_pool() -> None:
    global pool
    if pool is None:
        pool = MySQLPool()
        # Ensure users table exists
        try:
            with pool.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            email VARCHAR(255) NOT NULL UNIQUE,
                            password_hashed VARCHAR(255) NOT NULL,
                            role VARCHAR(50) NOT NULL,
                            phone VARCHAR(20) NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    
                    # Add phone column if it doesn't exist (migration)
                    cur.execute(
                        """
                        ALTER TABLE users 
                        ADD COLUMN IF NOT EXISTS phone VARCHAR(20) NULL
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS assignments (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            worker_id INT NOT NULL,
                            recruiter_id INT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY uq_worker (worker_id),
                            CONSTRAINT fk_assign_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE CASCADE,
                            CONSTRAINT fk_assign_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS tasks (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            recruiter_id INT NOT NULL,
                            worker_id INT NOT NULL,
                            title VARCHAR(200) NOT NULL,
                            description TEXT,
                            status ENUM('todo','in_progress','done') DEFAULT 'todo',
                            priority ENUM('low','medium','high') DEFAULT 'medium',
                            due_date DATE NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT fk_task_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE,
                            CONSTRAINT fk_task_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS time_logs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            worker_id INT NOT NULL,
                            check_in DATETIME NULL,
                            check_out DATETIME NULL,
                            work_date DATE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY uq_worker_date (worker_id, work_date),
                            CONSTRAINT fk_timelog_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS global_sessions (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            worker_id INT NOT NULL,
                            start_at DATETIME NOT NULL,
                            end_at DATETIME NULL,
                            paused BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT fk_gs_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    
                    # Add paused column if it doesn't exist (migration)
                    cur.execute(
                        """
                        ALTER TABLE global_sessions 
                        ADD COLUMN IF NOT EXISTS paused BOOLEAN DEFAULT FALSE
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS task_sessions (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            task_id INT NOT NULL,
                            worker_id INT NOT NULL,
                            start_at DATETIME NOT NULL,
                            end_at DATETIME NULL,
                            paused BOOLEAN DEFAULT FALSE,
                            keystrokes INT DEFAULT 0,
                            mouse_clicks INT DEFAULT 0,
                            mouse_moves INT DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT fk_ts_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    
                    # Add paused column if it doesn't exist (migration)
                    cur.execute(
                        """
                        ALTER TABLE task_sessions 
                        ADD COLUMN IF NOT EXISTS paused BOOLEAN DEFAULT FALSE
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS end_of_day_reports (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            worker_id INT NOT NULL,
                            recruiter_id INT NOT NULL,
                            work_date DATE NOT NULL DEFAULT (CURDATE()),
                            accomplishments TEXT,
                            challenges TEXT,
                            blockers TEXT,
                            hours INT DEFAULT 0,
                            next_day_plan TEXT,
                            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT fk_eod_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE CASCADE,
                            CONSTRAINT fk_eod_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    # Add recruiter_id column if table already existed
                    try:
                        cur.execute("ALTER TABLE end_of_day_reports ADD COLUMN recruiter_id INT")
                        # Update existing records with recruiter_id from assignments
                        cur.execute("""
                            UPDATE end_of_day_reports eod 
                            JOIN assignments a ON eod.worker_id = a.worker_id 
                            SET eod.recruiter_id = a.recruiter_id 
                            WHERE eod.recruiter_id IS NULL
                        """)
                        # Set default for any remaining NULL values
                        cur.execute("UPDATE end_of_day_reports SET recruiter_id = 1 WHERE recruiter_id IS NULL")
                        # Now make it NOT NULL
                        cur.execute("ALTER TABLE end_of_day_reports MODIFY COLUMN recruiter_id INT NOT NULL")
                        cur.execute("ALTER TABLE end_of_day_reports ADD CONSTRAINT fk_eod_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE")
                        conn.commit()
                    except Exception as e:
                        print(f"Error adding recruiter_id column: {e}")
                        pass
                    # Add new EOD fields if table existed before
                    try:
                        cur.execute("ALTER TABLE end_of_day_reports ADD COLUMN learned_today TEXT")
                        cur.execute("ALTER TABLE end_of_day_reports ADD COLUMN need_help_with TEXT")
                        conn.commit()
                    except Exception:
                        pass
                    # Create support tickets table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS support_tickets (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            worker_id INT NOT NULL,
                            category ENUM('time_tracking','attendance','task_tracking','technical','general') NOT NULL,
                            subject VARCHAR(200) NOT NULL,
                            description TEXT NOT NULL,
                            priority ENUM('low','medium','high') DEFAULT 'medium',
                            status ENUM('open','in_progress','resolved','closed') DEFAULT 'open',
                            admin_response TEXT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            CONSTRAINT fk_support_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )

                    # Create support_conversations table for threaded conversations
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS support_conversations (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            ticket_id INT NOT NULL,
                            sender_id INT NOT NULL,
                            sender_role ENUM('worker','admin') NOT NULL,
                            message TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT fk_conversation_ticket FOREIGN KEY (ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE,
                            CONSTRAINT fk_conversation_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    # Best-effort add status column if table existed before
                    try:
                        cur.execute("ALTER TABLE tasks ADD COLUMN status ENUM('todo','in_progress','done') DEFAULT 'todo'")
                        conn.commit()
                    except Exception:
                        pass
                    # Helpful indexes (ignore if exist)
                    for stmt in [
                        "ALTER TABLE users ADD INDEX idx_users_role (role)",
                        "ALTER TABLE users ADD INDEX idx_users_email (email)",
                        "ALTER TABLE tasks ADD INDEX idx_tasks_worker (worker_id)",
                        "ALTER TABLE tasks ADD INDEX idx_tasks_worker_status (worker_id, status)",
                        "ALTER TABLE assignments ADD INDEX idx_assign_recruiter (recruiter_id)",
                        "ALTER TABLE assignments ADD INDEX idx_assign_worker (worker_id)",
                        "ALTER TABLE global_sessions ADD INDEX idx_gs_worker_open (worker_id, end_at)",
                        "ALTER TABLE task_sessions ADD INDEX idx_ts_worker_task_open (worker_id, task_id, end_at)",
                        "ALTER TABLE support_tickets ADD INDEX idx_support_worker_status (worker_id, status)",
                        "ALTER TABLE support_tickets ADD INDEX idx_support_created (created_at)",
                        "ALTER TABLE support_conversations ADD INDEX idx_conversation_ticket (ticket_id, created_at)",
                        "ALTER TABLE support_conversations ADD INDEX idx_conversation_sender (sender_id, sender_role)",
                    ]:
                        try:
                            cur.execute(stmt)
                            conn.commit()
                        except Exception:
                            pass
                    conn.commit()
        except Error:
            # Let app startup continue; ping will reveal status
            pass


def ping_db() -> bool:
    if pool is None:
        init_pool()
    assert pool is not None
    try:
        with pool.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Error:
        return False


