from flask import Flask, request, abort

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

if __name__ == '__main__':
    app.run(port=8000)
