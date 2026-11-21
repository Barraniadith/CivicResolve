import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "civic_resolve.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        location_name TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        image_url TEXT,
        citizen_name TEXT DEFAULT 'Anonymous Citizen',
        citizen_phone TEXT,
        category TEXT NOT NULL,
        urgency TEXT DEFAULT 'Medium',
        public_impact_score INTEGER DEFAULT 3,
        department TEXT NOT NULL,
        ai_confidence REAL DEFAULT 0.85,
        ai_reasoning TEXT,
        status TEXT DEFAULT 'Reported',
        assigned_officer TEXT,
        resolution_notes TEXT,
        resolution_image_url TEXT,
        upvotes INTEGER DEFAULT 1,
        satisfaction_rating INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Ensure upvotes and satisfaction_rating exist if table was created previously
    cursor.execute("PRAGMA table_info(complaints)")
    cols = [r[1] for r in cursor.fetchall()]
    if "upvotes" not in cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN upvotes INTEGER DEFAULT 1")
    if "satisfaction_rating" not in cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN satisfaction_rating INTEGER")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT DEFAULT 'System',
        details TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaint_status ON complaints(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaint_urgency ON complaints(urgency);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_complaint ON audit_logs(complaint_id);")

    conn.commit()
    conn.close()

# Database Helper Functions
def fetch_all_complaints(
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if status and isinstance(status, str) and status != "All":
        query += " AND status = ?"
        params.append(status)
    if urgency and isinstance(urgency, str) and urgency != "All":
        query += " AND urgency = ?"
        params.append(urgency)
    if department and isinstance(department, str) and department != "All":
        query += " AND department = ?"
        params.append(department)
    if search and isinstance(search, str):
        s = f"%{search.strip()}%"
        query += " AND (title LIKE ? OR description LIKE ? OR location_name LIKE ? OR id LIKE ?)"
        params.extend([s, s, s, s])

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        d = dict(r)
        d["logs"] = fetch_audit_logs(d["id"], conn)
        results.append(d)

    conn.close()
    return results

def fetch_complaint_by_id(complaint_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    res = dict(row)
    res["logs"] = fetch_audit_logs(complaint_id, conn)
    conn.close()
    return res

def fetch_audit_logs(complaint_id: str, conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs WHERE complaint_id = ? ORDER BY id DESC", (complaint_id,))
    rows = cursor.fetchall()
    logs = [dict(r) for r in rows]

    if close_conn:
        conn.close()
    return logs

def insert_complaint(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    if "upvotes" not in data:
        data["upvotes"] = 1
    if "satisfaction_rating" not in data:
        data["satisfaction_rating"] = None

    cursor.execute("""
    INSERT INTO complaints (
        id, title, description, location_name, latitude, longitude, image_url,
        citizen_name, citizen_phone, category, urgency, public_impact_score,
        department, ai_confidence, ai_reasoning, status, assigned_officer,
        resolution_notes, resolution_image_url, upvotes, satisfaction_rating,
        created_at, updated_at
    ) VALUES (
        :id, :title, :description, :location_name, :latitude, :longitude, :image_url,
        :citizen_name, :citizen_phone, :category, :urgency, :public_impact_score,
        :department, :ai_confidence, :ai_reasoning, :status, :assigned_officer,
        :resolution_notes, :resolution_image_url, :upvotes, :satisfaction_rating,
        :created_at, :updated_at
    )
    """, data)

    conn.commit()
    conn.close()
    return fetch_complaint_by_id(data["id"])

def insert_audit_log(complaint_id: str, action: str, actor: str, details: str, timestamp: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    ts = timestamp or datetime.utcnow().isoformat()
    cursor.execute("""
    INSERT INTO audit_logs (complaint_id, action, actor, details, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (complaint_id, action, actor, details, ts))
    conn.commit()
    conn.close()

def update_complaint_fields(complaint_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    updates["updated_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    params = list(updates.values()) + [complaint_id]

    cursor.execute(f"UPDATE complaints SET {set_clause} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return fetch_complaint_by_id(complaint_id)

def upvote_complaint(complaint_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET upvotes = COALESCE(upvotes, 1) + 1 WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()
    insert_audit_log(
        complaint_id=complaint_id,
        action="COMMUNITY_UPVOTE",
        actor="Citizen (Community)",
        details="Neighbor confirmed impact. Upvote recorded (+1)."
    )
    return fetch_complaint_by_id(complaint_id)

def rate_complaint_resolution(complaint_id: str, rating: int, feedback: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET satisfaction_rating = ? WHERE id = ?", (rating, complaint_id))
    conn.commit()
    conn.close()
    insert_audit_log(
        complaint_id=complaint_id,
        action="CITIZEN_RATING",
        actor="Citizen",
        details=f"Citizen rated resolution satisfaction: {rating}/5 stars. Feedback: {feedback or 'Verified completed'}"
    )
    return fetch_complaint_by_id(complaint_id)

def get_stats_data() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Reported'")
    reported = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE urgency = 'Critical'")
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE urgency = 'High'")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT department, COUNT(*) FROM complaints GROUP BY department")
    dept_rows = cursor.fetchall()
    dept_breakdown = {r[0]: r[1] for r in dept_rows}

    cursor.execute("SELECT category, COUNT(*) FROM complaints GROUP BY category")
    cat_rows = cursor.fetchall()
    cat_breakdown = {r[0]: r[1] for r in cat_rows}

    cursor.execute("SELECT AVG(satisfaction_rating) FROM complaints WHERE satisfaction_rating IS NOT NULL")
    avg_sat_row = cursor.fetchone()[0]
    avg_satisfaction = round(avg_sat_row, 1) if avg_sat_row else 4.8

    conn.close()
    return {
        "total_complaints": total,
        "reported_count": reported,
        "in_progress_count": in_progress,
        "resolved_count": resolved,
        "critical_count": critical,
        "high_count": high,
        "department_breakdown": dept_breakdown,
        "category_breakdown": cat_breakdown,
        "avg_satisfaction": avg_satisfaction
    }

def count_complaints() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    c = cursor.fetchone()[0]
    conn.close()
    return c
