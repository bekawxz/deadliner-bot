import sqlite3

def init_db():
    conn = sqlite3.connect('deadliner.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            description TEXT,
            deadline TEXT
        )
    ''')

    conn.commit()
    conn.close()

def add_task(user_id, description, deadline):
    conn = sqlite3.connect('deadliner.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, description, deadline) VALUES(?,?,?)", (user_id, description, deadline))
    conn.commit()
    conn.close()

def list_tasks(user_id):
    conn = sqlite3.connect('deadliner.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, deadline FROM tasks WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_task(user_id, task_id):
    conn = sqlite3.connect('deadliner.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE user_id = ? AND id = ?", (user_id, task_id))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def edit_description(new_description,id,user_id):
    conn = sqlite3.connect('deadliner.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET description = ? WHERE id = ? AND user_id = ?", (new_description,id,user_id))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count
def edit_deadline(new_deadline,id,user_id):
    conn = sqlite3.connect('deadliner.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET deadline = ? WHERE id = ? AND user_id = ?", (new_deadline,id,user_id))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count