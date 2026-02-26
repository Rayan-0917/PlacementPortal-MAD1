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

if __name__ == "__main__":
    app.run(debug=True)
