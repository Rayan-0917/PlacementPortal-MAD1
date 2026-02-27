from flask import Flask, render_template, url_for, redirect
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registerStudent', methods=['GET', 'POST'])
def registerStudent():
    return render_template('registerStudent.html')

@app.route('/registerCompany', methods=['GET', 'POST'])
def registerCompany():
    return render_template('registerCompany.html')

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
