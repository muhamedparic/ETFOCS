from flask import Flask, request, abort, render_template

import json

import dbfunctions as db
import utils

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def api_login():
    if 'username' not in request.form or 'password' not in request.form:
        return json.dumps({'success': False, 'reason': 'Username or password not provided'})
    username = request.form.get('username')
    password = request.form.get('password')
    token, success = db.login(username, password)
    if success:
        return json.dumps({'success': True, 'token': token})
    else:
        return json.dumps({'success': False, 'reason': 'Invalid username or password'})

@app.route('/api/token_valid', methods=['POST'])
def api_token_valid():
    if 'token' not in request.form or not utils.valid_json(request.form.get('token')):
    	return 'false'
    return_value = db.token_valid(request.form.get('token'))
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

@app.route('/admin_profile')
def admin_profile():
	return render_template('admin-profile-dashboard.html')

#@app.route('/test_db')
def test_db():
	return str(oracle_test.oracle_test('users'))

# FIX
@app.route('/api/add_competition', methods=['POST'])
def api_add_competition():
	#if 'token' not in request.form or not utils.valid_json(request.form.get('token')) or not db.token_valid(request.form.get('token')): POPRAVI
	#	return json.dumps({'success': False, 'reason': 'Invalid token'}) POPRAVI
	if not 'name' in request.form or not 'type' in request.form or not 'subject' in request.form:
		return json.dumps({'success': False, 'reason': 'Missing competition info'})
	comp_name = request.form.get('name')
	comp_type = request.form.get('type')
	comp_subject = request.form.get('subject')
	#token = json.loads(request.form.get('token')) POPRAVI
	#username, _ = token['token'].split('.')
	username = 'muhamed' # POPRAVI
	# Dodaj da mora biti admin
	db.add_competition(comp_name, comp_type, comp_subject, username)
	return json.dumps({'success': True})

@app.route('/api/competition_list', methods=['POST'])
def api_competition_list():
    if not 'token' in request.form or db.get_token_info(request.form.get('token'))[2] != 'admin':
        return 'Invalid token!'
    return db.competition_list()

@app.route('/api/add_question', methods=['POST'])
def api_add_question():
    required_fields = ('token', 'type', 'competition', 'question_data', 'answer_data')
    if not all(field in request.form for field in required_fields):
        return {'success': False, 'reason': 'Missing one or more fields'}
    return db.add_question(request.form.get('token'), request.form.get('type'),
                           request.form.get('competition'), request.form.get('question_data'),
                           request.form.get('answer_data'))

@app.route('/api/add_file', methods=['POST'])
def api_add_file():
    pass

@app.route('/api/remove_question', methods=['POST'])
def api_remove_question():
    pass

@app.route('/api/submit_solution', methods=['POST'])
def api_submit_solution():
    pass

@app.route('/api/submit_answers', methods=['POST'])
def api_submit_answers():
    pass

@app.route('/api/competition_questions', methods=['POST'])
def api_competition_questions():
    pass

@app.route('/api/competition_info', methods=['POST'])
def api_competition_info():
    pass

if __name__ == '__main__':
    try:
    	app.run(host='192.168.0.19', port=8000, processes=4)
    except OSError:
    	app.run(host='localhost', port=8000, processes=4)
