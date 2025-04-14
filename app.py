#Corresponde al archivo que va a contener el código de flask

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'


#Creación de la base de datos

def init_db():
    if not os.path.exists('users.db'):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
                  CREATE TABLE users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL
                  )
                  ''')
        
def init_planes_db():
        if not os.path.exists('planes.db'):
            conn = sqlite3.connect('planes.db')
            c = conn.cursor()  
            c.execute('''
                  CREATE TABLE planes (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  titulo TEXT NOT NULL,
                  descripcion TEXT,
                  responsable TEXT,
                  fecha_compromiso TEXT,
                  estado TEXT
                  )
                  ''')
            conn.commit()
            conn.close()        
        

        #USUARIO MAESTRO
        c.execute('''
                  INSERT INTO users (username, password, role)
                  VALUES (?,?,?)
                  ''',('admin','admin123','maestro'))
        conn.commit()
        conn.close()



#Página de inicio de sesión

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (user, pwd))
        data = c.fetchone()
        conn.close()
        if data:
            session['user'] = data[1]
            session['role'] = data[3]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')


# Página principal después de iniciar sesión
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'], role=session['role'])

@app.route('/planes')
def ver_planes():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM planes')
    planes = c.fetchall()
    conn.close()
    return render_template('planes.html',planes=planes)

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#Ruta para crear un nuevo plan de acción
@app.route('/nuevo', methods=['GET','POST'])
def nuevo_plan():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        responsable = request.form['responsable']
        fecha = request.form['fecha_compromiso']
        estado = request.form['estado']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
                  INSERT INTO planes (titulo, descripcion, responsable, fecha_compromiso, estado)
                  VALUES (?,?,?,?,?)
                  ''', (titulo, descripcion, responsable, fecha, estado))
        conn.commit()
        conn.close()
        return redirect(url_for('ver_planes'))
    return render_template('nuevo_plan.html')

   

if __name__ == '__main__':
    init_db()
    init_planes_db()
    app.run(debug=True)
