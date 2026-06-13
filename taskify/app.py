from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_secure_key'

# MySQL Config (XAMPP default settings)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'taskify_db'

mysql = MySQL(app)

def get_db_cursor(dict_cursor=False):
    if dict_cursor:
        return mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    return mysql.connection.cursor()

# Home - show tasks
@app.route('/')
def index():
    cur = get_db_cursor(dict_cursor=True)
    cur.execute("SELECT * FROM tasks ORDER BY due_date")
    tasks = cur.fetchall()
    cur.close()
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

    cur = get_db_cursor()
    cur.execute(
        "INSERT INTO tasks(title, description, due_date, priority) VALUES(%s, %s, %s, %s)",
        (title, description, due_date, priority)
    )
    mysql.connection.commit()
    cur.close()

    flash('Task added successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit(id):
    cur = get_db_cursor(dict_cursor=True)
    cur.execute("SELECT * FROM tasks WHERE id=%s", (id,))
    task = cur.fetchone()

    if not task:
        cur.close()
        flash('Task not found.', 'error')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM tasks ORDER BY due_date")
    tasks = cur.fetchall()
    cur.close()
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

    cur = get_db_cursor()
    cur.execute(
        "UPDATE tasks SET title=%s, description=%s, due_date=%s, priority=%s WHERE id=%s",
        (title, description, due_date, priority, id)
    )
    mysql.connection.commit()
    cur.close()

    flash('Task updated successfully.', 'success')
    return redirect(url_for('index'))

# Delete task
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = get_db_cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Task deleted successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)