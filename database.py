import sqlite3
import hashlib
import datetime

DATABASE_NAME = 'noesis_db.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discipline_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (discipline_id) REFERENCES disciplines(id) ON DELETE CASCADE,
            UNIQUE(discipline_id, name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT,
            file_path TEXT,
            discipline_id INTEGER,
            lesson_id INTEGER DEFAULT -1,
            description TEXT,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (discipline_id) REFERENCES disciplines(id) ON DELETE SET NULL,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS full_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            start_datetime DATETIME NOT NULL,
            end_datetime DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            is_completed BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, hashed_password, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_id_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

def get_user_details_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, is_admin FROM users WHERE username = ?", (username,))
    user_details = cursor.fetchone()
    conn.close()
    return user_details

def add_discipline(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO disciplines (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_disciplines():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM disciplines ORDER BY name ASC")
    disciplines = cursor.fetchall()
    conn.close()
    return disciplines

def get_discipline_name(discipline_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM disciplines WHERE id = ?", (discipline_id,))
    name = cursor.fetchone()
    conn.close()
    return name[0] if name else "N/A"

def update_discipline(discipline_id, new_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE disciplines SET name = ? WHERE id = ?", (new_name, discipline_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_discipline(discipline_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM disciplines WHERE id = ?", (discipline_id,))
    conn.commit()
    conn.close()

def add_lesson(discipline_id, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO lessons (discipline_id, name) VALUES (?, ?)", (discipline_id, name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_lessons_by_discipline(discipline_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM lessons WHERE discipline_id = ? ORDER BY name ASC", (discipline_id,))
    lessons = cursor.fetchall()
    conn.close()
    return lessons

def get_lesson_name(lesson_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM lessons WHERE id = ?", (lesson_id,))
    name = cursor.fetchone()
    conn.close()
    return name[0] if name else ""

def add_material(title, material_type, file_path, discipline_id, lesson_id, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO materials (title, type, file_path, discipline_id, lesson_id, description) VALUES (?, ?, ?, ?, ?, ?)",
                   (title, material_type, file_path, discipline_id, lesson_id, description))
    conn.commit()
    conn.close()

def get_materials():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            m.id, 
            m.title, 
            m.type, 
            m.file_path, 
            m.discipline_id, 
            m.lesson_id, 
            m.description, 
            m.uploaded_at 
        FROM materials m
        ORDER BY m.uploaded_at DESC
    ''')
    materials = cursor.fetchall()
    conn.close()
    return materials

def get_material_by_id(material_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, type, file_path, discipline_id, lesson_id, description FROM materials WHERE id = ?", (material_id,))
    material = cursor.fetchone()
    conn.close()
    return material

def update_material(material_id, title, material_type, file_path, discipline_id, lesson_id, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE materials SET title = ?, type = ?, file_path = ?, discipline_id = ?, lesson_id = ?, description = ? WHERE id = ?",
                   (title, material_type, file_path, discipline_id, lesson_id, description, material_id))
    conn.commit()
    conn.close()

def delete_material(material_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()

def add_note(user_id, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (user_id, content) VALUES (?, ?)", (user_id, content))
    conn.commit()
    conn.close()

def get_notes(user_id, limit=5):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM notes WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
    notes = cursor.fetchall()
    conn.close()
    return notes

def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

def add_full_note(user_id, title, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO full_notes (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
    conn.commit()
    conn.close()

def get_full_notes(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, created_at, updated_at FROM full_notes WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes

def update_full_note(note_id, title, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE full_notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (title, content, note_id))
    conn.commit()
    conn.close()

def delete_full_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM full_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

def add_event(user_id, title, description, start_datetime, end_datetime=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (user_id, title, description, start_datetime, end_datetime) VALUES (?, ?, ?, ?, ?)",
                   (user_id, title, description, start_datetime, end_datetime))
    conn.commit()
    conn.close()

def get_events(user_id, start_date=None, end_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, title, description, start_datetime, end_datetime FROM events WHERE user_id = ?"
    params = [user_id]
    if start_date:
        query += " AND start_datetime >= ?"
        params.append(start_date)
    if end_date:
        query += " AND start_datetime <= ?"
        params.append(end_date)
    query += " ORDER BY start_datetime ASC"
    cursor.execute(query, params)
    events = cursor.fetchall()
    conn.close()
    return events

def update_event(event_id, title, description, start_datetime, end_datetime):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET title = ?, description = ?, start_datetime = ?, end_datetime = ? WHERE id = ?",
                   (title, description, start_datetime, end_datetime, event_id))
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()

def add_task(user_id, title, description, due_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, description, due_date) VALUES (?, ?, ?, ?)",
                   (user_id, title, description, due_date))
    conn.commit()
    conn.close()

def get_tasks(user_id, include_completed=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_completed:
        cursor.execute("SELECT id, title, description, due_date, is_completed, created_at FROM tasks WHERE user_id = ? ORDER BY due_date ASC, created_at DESC", (user_id,))
    else:
        cursor.execute("SELECT id, title, description, due_date, is_completed, created_at FROM tasks WHERE user_id = ? AND is_completed = 0 ORDER BY due_date ASC, created_at DESC", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task(task_id, title, description, due_date, is_completed):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = ?, description = ?, due_date = ?, is_completed = ? WHERE id = ?",
                   (title, description, due_date, is_completed, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def mark_task_completed(task_id, is_completed=True):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET is_completed = ? WHERE id = ?", (1 if is_completed else 0, task_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    print("Tabelas criadas ou já existentes no banco de dados.")
