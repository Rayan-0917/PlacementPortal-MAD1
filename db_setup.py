import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn=sqlite3.connect('placement.db')
    cursor=conn.cursor()

    #users table-roles
    cursor.execute(''' create table if not exists users (
        id integer primary key autoincrement,
        username text unique not null,
        password text not null,
        role text not null,
        is_approved integer default 0
        is_blacklisted integer default 0    
    ) ''')

    #companies
    cursor.execute(''' create table if not exists companies (
        id integer primary key autoincrement,
        user_id integer,
        company_name text,
        hr_contact text,
        website text,
        description text,
        foreign key(user_id) references users (id)               
    )''')

    #students 
    cursor.execute(''' create table if not exists students (
        id integer primary key autoincrement,
        user_id integer,
        student_name text,
        email text,
        department text,
        resume_url text,  
        foreign key(user_id) references users (id)             
    ) ''')

    #placement drives table
    cursor.execute(''' create table if not exists drives (
            id integer primary key autoincrement,
            company_id integer,
            drive_name text,
            job_title text,
            job_description text,
            salary text,
            eligibility text,
            deadline text,
            is_approved integer default 0,
            is_closed integer default 0,
            foreign key(company_id) references companies (id)        
        ) ''')
    
    #student applications table
    cursor.execute(''' create table if not exists applications (
            id integer primary key autoincrement,
            student_id integer,
            drive_id integer,
            status text default 'Applied',
            date_applied datetime default CURRENT_TIMESTAMP,
            unique(student_id, drive_id),
            foreign key(student_id) references students (id),
            foreign key(drive_id) references drives (id)          
        ) ''')
    
    
    #admin user
    admin_password=generate_password_hash('admin123')
    try:
        cursor.execute("insert into users (username, password, role, is_approved) values (?, ?, ?, ?)" , ("admin", admin_password, "Admin", 1))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()

if __name__=='__main__':
    init_db()