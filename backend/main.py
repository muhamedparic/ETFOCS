from flask import Flask, request, abort, render_template

import json

import dbfunctions as db

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def api_login():
    if 'username' not in request.form or 'password' not in request.form:
        return json.dumps({'success': False, 'reason': 'Username or password not provided'})
    username = request.form.get('username')
    password = request.form.get('password')
    result, success = db.login(username, password)
    if success:
        return json.dumps({'success': True, 'token': result})
    else:
        return json.dumps({'success': False, 'reason': 'Invalid username or password'})

@app.route('/api/token_valid')
def api_token_valid():
    return 'token' in request.form and db.token_valid(request.form.get('token'))

@app.route('/')
@app.route('/main')
def index():
	return render_template('main.html')

@app.route('/home')
def home():
	return render_template('homepage.html')

@app.route('/profile')
def profile():
	return render_template('profile-dashboard.html')

if __name__ == '__main__':
    app.run(port=8000)
