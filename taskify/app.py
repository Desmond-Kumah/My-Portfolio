from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_secure_key'

# SQLite Config
DATABASE = os.path.join(os.path.dirname(__file__), 'taskify.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# Initialize database on startup
init_db()

# Home - show tasks
@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY due_date").fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# Add task
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_date = request.form.get('due_date', '').strip()
    priority = request.form.get('priority', '').strip()

    if not title or not description or not due_date or not priority:
        flash('All fields are required.', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks(title, description, due_date, priority) VALUES(?, ?, ?, ?)",
        (title, description, due_date, priority)
    )
    conn.commit()
    conn.close()

    flash('Task added successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit(id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (id,)).fetchone()

    if not task:
        conn.close()
        flash('Task not found.', 'error')
        return redirect(url_for('index'))

    tasks = conn.execute("SELECT * FROM tasks ORDER BY due_date").fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks, edit_task=task)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_date = request.form.get('due_date', '').strip()
    priority = request.form.get('priority', '').strip()

    if not title or not description or not due_date or not priority:
        flash('All fields are required.', 'error')
        return redirect(url_for('edit', id=id))

    conn = get_db_connection()
    conn.execute(
        "UPDATE tasks SET title=?, description=?, due_date=?, priority=? WHERE id=?",
        (title, description, due_date, priority, id)
    )
    conn.commit()
    conn.close()

    flash('Task updated successfully.', 'success')
    return redirect(url_for('index'))

# Delete task
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash('Task deleted successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)