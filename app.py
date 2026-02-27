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

#all admin routes

#admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if(session.get('role')!='Admin'):
        return redirect(url_for('login'))
    
    db=get_db()

    all_students=db.execute('select s.*, u.is_blacklisted from students s join users u on s.user_id=u.id').fetchall()
    all_companies=db.execute('select c.*, u.is_blacklisted from companies c join users u on c.user_id=u.id').fetchall()

    pending_companies=db.execute('select u.id, c.company_name from users u join companies c on u.id=c.user_id where u.is_approved=0').fetchall()

    db.close()
    return render_template('admin_dashboard.html', all_students=all_students, all_companies=all_companies, pending_companies=pending_companies)

#approve company
@app.route('/admin/approve_company/<int:uid>')
def approve_company(uid):
    if(session['role']!='Admin'):
        return redirect(url_for('login'))
    db=get_db()
    db.execute('update users set is_approved=1 where id=?', (uid, ))
    db.commit()
    db.close()
    return redirect(url_for('admin_dashboard'))

#blacklist user
@app.route('/admin/blacklist/<int:uid>')
def toggle_blacklist(uid):
    if(session['role']!='Admin'):
        return redirect(url_for('login'))
    db=get_db()
    user=db.execute('select is_blacklisted from users where id=?', (uid, )).fetchone()
    new_status=0
    if(user['is_blacklisted']):
        new_status=0
    else:
        new_status=1
    db.execute('update users set is_blacklisted=? where id=?', (new_status, uid))
    db.commit()
    db.close()
    flash('User status updated')
    return redirect(url_for('admin_dashboard'))

#all student routes

#student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

#all company routes

#company dashboard
@app.route('/company_dashboard')
def company_dashboard():
    return render_template('company_dashboard.html')

#create drive
@app.route('/create_drive', methods=['GET', 'POST'])
def create_drive():
    if(session.get('role')!='Company'):
        return redirect(url_for('login'))
    if(request.method=='POST'):
        db=get_db()
        company=db.execute('select id from companies where user_id=?', (session['user_id'],)).fetchone()
        db.execute('insert into drives (company_id, drive_name, job_title, job_description, salary, deadline, eligibility) values (?, ?, ?, ?, ?, ?, ?)', (company['id'], request.form['name'], request.form['title'], request.form['desc'], request.form['salary'], request.form['deadline'], request.form['eligibility']))
        db.commit()
        db.close()
        flash('Drive created! Waiting for admin approval')
        return redirect(url_for('company_dashboard'))
    return render_template('create_drive.html')

if __name__ == "__main__":
    app.run(debug=True)
