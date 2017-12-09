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

@app.route('/edit_competition_fill')
def edit_competition_fill():
    return render_template('edit-competition-fill.html')

@app.route('/edit_competition_code')
def edit_competition_code():
    return render_template('edit-competition-code.html')

@app.route('/edit_competition_multiple_choice')
def edit_competition_multiple_choice():
    return render_template('edit-competition-multiple-choice.html')

# FIX
@app.route('/api/add_competition', methods=['POST'])
def api_add_competition():
    required_fields = ('token', 'type', 'name')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.add_competition(request.form.get('token'), request.form.get('type'),
                              request.form.get('name'))

@app.route('/api/competition_list', methods=['POST'])
def api_competition_list():
    required_fields = ('token',)
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.get_competition_list(request.form.get('token'))

@app.route('/api/add_question', methods=['POST'])
def api_add_question():
    required_fields = ('token', 'type', 'competition', 'question_data', 'answer_data')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.add_question(request.form.get('token'), request.form.get('type'),
                           request.form.get('competition'), request.form.get('question_data'),
                           request.form.get('answer_data'))

@app.route('/api/remove_question', methods=['POST'])
def api_remove_question():
    required_fields = ('token', 'competition', 'question')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.remove_question(request.form.get('token'), request.form.get('competition'),
                              request.form.get('question'))

@app.route('/api/submit_solution', methods=['POST'])
def api_submit_solution():
    pass

@app.route('/api/submit_answer', methods=['POST'])
def api_submit_answer():
    required_fields = ('token', 'competition', 'question', 'answer')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.submit_answer(request.form.get('token'), request.form.get('competition'),
                            request.form.get('question'), request.form.get('answer'))

@app.route('/api/add_competitor', methods=['POST'])
def api_add_competitor():
    required_fields = ('token', 'competition', 'user')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.add_competitor(request.form.get('token'), request.form.get('competition'),
                             request.form.get('user'))

@app.route('/api/competition_questions', methods=['POST'])
def api_competition_questions():
    pass

@app.route('/api/competition_results', methods=['POST'])
def api_competition_info():
    pass

@app.route('/api/add_task_file', methods=['POST'])
def api_add_task_file():
    pass

@app.route('/secret/gitpull', methods=['GET'])
def secret_gitpull():
    utils.gitpull()
    return ""

if __name__ == '__main__':
    try:
    	app.run(host='192.168.0.19', port=8000, processes=4)
    except OSError:
    	app.run(host='localhost', port=8000, processes=4)
