from flask import Flask, request, abort, render_template

import json

import dbfunctions as db
import oracle_test
import utils

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

@app.route('/api/token_valid', methods=['POST'])
def api_token_valid():
    if 'token' not in request.form or not utils.valid_json(request.form.get('token')):
    	return 'false'
    return_value = db.token_valid(request.form.get('token'))
    print(request.form.get('token'), return_value)
    return 'true' if return_value else 'false'

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

@app.route('/test_db')
def test_db():
	return str(oracle_test.oracle_test('users'))

@app.route('/api/add_competition')
def api_add_competition():
	if 'token' not in request.form or not utils.valid_json(request.form.get('token')) or not db.token_valid(request.form.get('token')):
		return json.dumps({'success': False, 'reason': 'Invalid token'})
	if not 'name' in request.form or not 'type' in request.form or not 'subject' in request.form:
		return json.dumps({'success': False, 'reason': 'Missing competition info'})
	comp_name = request.form.get('name')
	comp_type = request.form.get('type')
	comp_subject = request.form.get('subject')
	token = json.loads(request.form.get('token'))
	username, _ = token['token'].split('.')
	dbfunctions.add_competition(comp_name, comp_type, comp_subject, username)
	return json.dumps({'success': True})

if __name__ == '__main__':
    app.run(host='192.168.0.20', port=8000, processes=4)
