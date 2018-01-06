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

@app.route('/edit_participants')
def edit_participants():
    return render_template('edit-participants.html')

@app.route('/competition_fill')
def competition_fill():
    return render_template('competition-fill.html')

@app.route('/competition_multiple_choice')
def competition_multiple_choice():
    return render_template('competition-multiple-choice.html')

@app.route('/competition_code')
def competition_code():
    return render_template('competition-code.html')

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

@app.route('/api/submit_answers', methods=['POST'])
def api_submit_answer():
    required_fields = ('token', 'competition', 'answers')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.submit_answers(request.form.get('token'), request.form.get('competition'),
                            request.form.get('answers'))

@app.route('/api/add_competitor', methods=['POST'])
def api_add_competitor():
    required_fields = ('token', 'competition', 'user')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.add_competitor(request.form.get('token'), request.form.get('competition'),
                             request.form.get('user'))

@app.route('/api/competition_questions', methods=['POST'])
def api_competition_questions():
    required_fields = ('token', 'competition')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.get_competition_questions(request.form.get('token'), request.form.get('competition'))

@app.route('/api/competition_results', methods=['POST'])
def api_competition_results():
    required_fields = ('token', 'competition')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.get_competition_results(request.form.get('token'), request.form.get('competition'))

@app.route('/api/add_task_file', methods=['POST'])
def api_add_task_file():
    required_fields = ('token', 'competition', 'name')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    file_data = request.files.get('filedata')
    filename = request.form.get('name') + '.pdf'
    return db.add_task_file(request.form.get('token'), request.form.get('competition'),
                            request.form.get('name'), file_data, filename)

@app.route('/api/download_task_file', methods=['POST'])
def api_download_task_file():
    required_fields = ('token', 'competition', 'name')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.download_task_file(request.form.get('token'), request.form.get('competition'),
                                 request.form.get('name'))

@app.route('/api/task_list', methods=['POST'])
def api_get_task_list():
    required_fields = ('token', 'competition')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.get_task_list(request.form.get('token'), request.form.get('competition'))

@app.route('/api/search_users', methods=['POST'])
def api_search_users():
    required_fields = ('token', 'username')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.search_users(request.form.get('token'), request.form.get('username'))

@app.route('/api/user_competitions', methods=['POST'])
def api_user_competitions():
    required_fields = ('token', 'username')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.get_user_competitions(request.form.get('token'), request.form.get('username'))

@app.route('/api/competition_participants', methods=['POST'])
def api_competition_participants():
    required_fields = ('token', 'competition')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.get_competition_participants(request.form.get('token'), request.form.get('competition'))

@app.route('/api/available_competition_list', methods=['POST'])
def api_available_competition_list():
    required_fields = ('token',)
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.get_available_competition_list(request.form.get('token'))

@app.route('/api/apply_for_competition', methods=['POST'])
def api_apply_for_competition():
    required_fields = ('token', 'competition')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.apply_for_competition(request.form.get('token'), request.form.get('competition'))

@app.route('/api/application_list_admin', methods=['POST'])
def api_application_list_admin():
    required_fields = ('token', 'competition')
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.application_list_admin(request.form.get('token'), request.form.get('competition'))

@app.route('/api/application_list_all', methods=['POST'])
def api_application_list_all():
    required_fields = ('token',)
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.application_list_all(request.form.get('token'))

@app.route('/api/number_of_competitors', methods=['POST'])
def api_number_of_competitors():
    required_fields = ('token',)
    if not all(field in request.form for field in required_fields):
        return json.dumps({'success': False, 'reason': 'Missing one or more fields'})
    return db.number_of_competitors(request.form.get('token'))

@app.route('/secret/gitpull', methods=['GET'])
def secret_gitpull():
    utils.gitpull()
    return ""

if __name__ == '__main__':
    try:
    	app.run(host='192.168.0.31', port=8000, processes=4)
    except OSError:
    	app.run(host='localhost', port=8000, processes=4)
