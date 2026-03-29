import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "smart_system_2026_ultra_key"

# --- BAZANI SOZLASH ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Foydalanuvchilar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  email TEXT, 
                  nickname TEXT, 
                  password TEXT, 
                  name TEXT, 
                  age INTEGER, 
                  bio TEXT, 
                  role TEXT DEFAULT 'user')''')
    # Vazifalar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  task_text TEXT)''')
    conn.commit()
    conn.close()

# Dastur ishga tushishi bilan bazani tekshiradi
init_db()

# --- YO'NALISHLAR (ROUTES) ---

@app.route('/')
def home():
    # Agar foydalanuvchi kirgan bo'lsa, dashboardga yuboradi
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Ro'yxatdan o'tish sahifasini ochish (404 xatosini davolaydi)
@app.route('/login_page')
def login_page():
    return render_template('login_auth.html')

# Ro'yxatdan o'tish jarayoni
@app.route('/login_action', methods=['POST'])
def login_action():
    email = request.form.get('email')
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    name = request.form.get('name')
    age = request.form.get('age')
    bio = request.form.get('bio')
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Birinchi foydalanuvchini admin qilish (ixtiyoriy)
        user_count = c.execute("SELECT count(*) FROM users").fetchone()[0]
        role = 'admin' if user_count == 0 else 'user'
        
        c.execute("INSERT INTO users (email, nickname, password, name, age, bio, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (email, nickname, password, name, age, bio, role))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home')) # Ro'yxatdan o'tgach login sahifasiga
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"

# Tizimga kirishni tekshirish (Auth)
@app.route('/auth', methods=['POST'])
def auth():
    nickname = request.form.get('nickname')
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = sqlite3.connect('database.db')
    user = conn.execute("SELECT * FROM users WHERE nickname=? AND email=? AND password=?", 
                        (nickname, email, password)).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['user_email'] = user[1]
        session['user_nickname'] = user[2]
        session['user_role'] = user[7]
        return redirect(url_for('dashboard'))
    
    return "Kirish ma'lumotlari xato! <a href='/'>Orqaga qaytish</a>"

# Asosiy ishchi maydon (Dashboard)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    conn = sqlite3.connect('database.db')
    # Faqat shu foydalanuvchiga tegishli vazifalarni olish
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id=?", (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('index.html', tasks=tasks)

# Vazifa qo'shish
@app.route('/add_task', methods=['POST'])
def add_task():
    task_text = request.form.get('task')
    if task_text and 'user_id' in session:
        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO tasks (user_id, task_text) VALUES (?, ?)", 
                     (session['user_id'], task_text))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

# Vazifani o'chirish
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        conn.execute("DELETE FROM tasks WHERE id=? AND user_id=?", 
                     (task_id, session['user_id']))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

# Tizimdan chiqish
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
