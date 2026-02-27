from flask import Flask, render_template, url_for, redirect, request, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key='Placement_secret_key'

def get_db():
    conn=sqlite3.connect('Placement.db')
    conn.row_factory=sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        db=get_db()
        user=db.execute('select * from users where email=?', (email,)).fetchone()
        db.close()

        if(user and check_password_hash(user['password'], password)):
            if(user['is_blacklisted']):
                flash('Your account is blacklisted. Contact admin for more info.')
                return redirect(url_for('login'))   
            
            session['user_id']=user['id']
            session['role']=user['role']
            session['username']=user['username']
            session['email']=user['email']

            if(user['role']=='Admin'):
                return redirect(url_for('admin_dashboard'))
            if(user['role']=='Company'):
                return redirect(url_for('company_dashboard'))
            if(user['role']=='Student'):
                return redirect(url_for('student_dashboard'))
        
        flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/registerStudent', methods=['GET', 'POST'])
def registerStudent():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        department=request.form['department']
        password=generate_password_hash(request.form['password'])
        role='Student'

        if role!='Student':
            return "Invaild Action", 403
        
        db=get_db()
        try:
            approved=1
            cur=db.execute('insert into users (username, password, email, role, is_approved) values (?, ?, ?, ?, ?)', (name, password, email, role, approved))
            user_id=cur.lastrowid

            db.execute('insert into students (user_id, student_name, email, department) values (?, ?, ?, ?)', (user_id, name, email, department))

            db.commit()
            flash('Registration Successful. You can login now.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already in use.')
        finally: 
            db.close()
    return render_template('registerStudent.html')

@app.route('/registerCompany', methods=['GET', 'POST'])
def registerCompany():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        website=request.form['website']
        password=generate_password_hash(request.form['password'])
        role='Company'

        if role!='Company':
            return "Invalid Action", 403
        db=get_db()
        try:
            approved=0
            cur=db.execute('insert into users (username, password, email, role, is_approved) values (?, ?, ?, ?, ?)', (name, password, email, role, approved))
            user_id=cur.lastrowid

            db.execute('insert into companies (user_id, company_name, hr_contact, website) values (?, ?, ?, ?)', (user_id, name, email, website))

            db.commit()
            flash('Registration successful. Wait for admin approval.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already in use.')
        finally:
            db.close()

    return render_template('registerCompany.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/company_dashboard')
def company_dashboard():
    return render_template('company_dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)
