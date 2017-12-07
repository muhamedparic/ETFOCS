import hashlib
import time
import random
import string
import json

import MySQLdb

import utils

conn = MySQLdb.connect(host='localhost', user='admin', password='root', db='ETFOCS')
char_set = string.ascii_letters + string.digits + string.punctuation
#secret_key = ''.join([random.choice(char_set) for _ in range(64)])
secret_key = '7725b1b3d5aa1b7af2f102463e12740519c50112a370e74fce3340c96e54b979'

def login(username, password):
    with conn.cursor() as cur:
        cur.execute('SELECT role FROM users WHERE username=%s AND password_hash=%s', (username, hashlib.sha256(password.encode('utf-8')).hexdigest()))
        result = cur.fetchone()
        if result is None:
            return None, False
        else:
            role = result[0]
            exp_at = str(int(time.time()) + 24 * 60 * 60)
            token = username + '.' + exp_at
            token_hash = hashlib.sha256((token + secret_key).encode('utf-8')).hexdigest()
            return {'token': token, 'role': role, 'hash': token_hash}, True

def register(username, password):
    with conn.cursor() as cur:
        cur.execute('INSERT INTO users(username, password_hash) VALUES (%s, %s)', (username, hashlib.sha256(password.encode('utf-8')).hexdigest()))
    conn.commit()
    return 'yos'

def user_exists(username):
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM users WHERE username=%s', (username,))
        return cur.fetchone() is not None

def is_admin_user(username):
	with conn.cursor() as cur:
		cur.execute('SELECT id FROM users WHERE username=%s AND admin=1', (username,))
		return cur.fetchone() is not None

def get_role(username):
    with conn.cursor() as cur:
        cur.execute('SELECT role FROM users WHERE username=%s', (username,))
        return cur.fetchone()[0]

def token_valid(token):
    token = json.loads(token)
    token_string = token['token']
    token_hash = token['hash']
    if hashlib.sha256((token_string + secret_key).encode('utf-8')).hexdigest() != token_hash:
        return False
    user, exp_at = token_string.split('.')
    exp_at = int(exp_at)
    if not user_exists(user):
        return False
    return exp_at > time.time()

# Returns valid (bool), user (str), role (str, "admin" or "user")
def get_token_info(token):
    if type(token) == str:
        try:
            token = json.loads(token)
        except:
            return False, None, None
    if type(token) != dict:
        return False, None, None
    if not all(key in token for key in ('token', 'hash', 'role')):
        return False, None, None
    token_string = token['token']
    token_hash = token['hash']
    if hashlib.sha256((token_string + secret_key).encode('utf-8')).hexdigest() != token_hash:
        return False, None, None
    user, exp_at = None, None
    try:
        user, exp_at = token_string.split('.')
        exp_at = int(exp_at)
    except:
        return False, None, None
    token_role = get_role(user)
    if token_role not in ('user', 'admin'):
        return False, None, None
    if not user_exists(user) or exp_at <= time.time():
        return False, None, None
    return True, user, token_role

def valid_competition(comp_type, comp_name):
    with conn.cursor() as cur:
        cur.execute("""SELECT COUNT(*) FROM competition_types AS ct
                       INNER JOIN competitions AS c ON ct.id=c.type_fk
                       WHERE ct.description=%s and c.name=%s""", (comp_type, comp_name))
        result = cur.fetchone()[0]
        return result == 1

def add_question(token, comp_type, comp_name, question_data, answer_data):
    token_info = get_token_info(token)
    if token_info[2] != 'admin':
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    if comp_type not in ('fill', 'multiple_choice'):
        return json.dumps({'success': False, 'reason': 'Invalid competition type'})
    if not valid_competition(comp_type, comp_name):
        return json.dumps({'success': False, 'reason': 'Invalid competition'})
    if not utils.valid_question_answer_data(comp_type, question_data, answer_data):
        return json.dumps({'success': False, 'reason': 'Invalid question or answer data'})
    user = token_info[1]
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO
                       questions(competition_fk, created_by_fk, question_data, answer_data)
                       VALUES
                       ((SELECT id FROM competitions WHERE name=%s),
                       (SELECT id FROM users WHERE username=%s),
                       %s,
                       %s)""", (comp_name, user, question_data, answer_data))
        conn.commit()
        if cur.rowcount != 1:
            raise Exception('Problem with INSERT')
    return json.dumps({'success': True})


def competition_list():
	with conn.cursor() as cur:
		cur.execute('SELECT name, type, subject FROM competitions')
		return json.dumps(cur.fetchall())
