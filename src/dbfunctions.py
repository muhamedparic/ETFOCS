import hashlib
import time
import random
import string
import json

import MySQLdb
from werkzeug.utils import secure_filename
from flask import send_from_directory

import utils

conn = MySQLdb.connect(host='localhost', user='admin', password='root', db='ETFOCS')
char_set = string.ascii_letters + string.digits + string.punctuation
secret_key = '7725b1b3d5aa1b7af2f102463e12740519c50112a370e74fce3340c96e54b979'
upload_folder = '/home/fajik/Desktop/ETFOCS/src/static/task_files'

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
    if type(token_string) != str:
        return False, None, None
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
                       WHERE ct.description=%s and c.name=%s
                       """, (comp_type, comp_name))
        result = cur.fetchone()[0]
        return result == 1

def add_competition(token, comp_type, comp_name):
    token_info = get_token_info(token)
    if token_info[2] != 'admin':
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    if len(comp_name) == 0:
        return json.dumps({'success': False, 'reason': 'Invalid competition'})
    if comp_type not in ('fill', 'multiple_choice', 'code'):
        return json.dumps({'success': False, 'reason': 'Invalid competition type'})
    with conn.cursor() as cur:
        try:
            cur.execute("""INSERT INTO
                           competitions(name, type_fk, created_by_fk)
                           VALUES
                           (%s,
                           (SELECT id FROM competition_types WHERE description=%s),
                           (SELECT id FROM users WHERE username=%s))
                           """, (comp_name, comp_type, token_info[1]))
            conn.commit()
        except:
            return json.dumps({'success': False, 'reason': 'Invalid competition'})
    return json.dumps({'success': True})

def add_question(token, comp_type, comp_name, question_data, answer_data):
    token_info = get_token_info(token)
    if token_info[2] != 'admin':
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    #if comp_type not in ('fill', 'multiple_choice'):
    #    return json.dumps({'success': False, 'reason': 'Invalid competition type'})
    if not valid_competition(comp_type, comp_name):
        return json.dumps({'success': False, 'reason': 'Invalid competition'})
    #if not utils.valid_question_answer_data(comp_type, question_data, answer_data):
    #    return json.dumps({'success': False, 'reason': 'Invalid question or answer data'})
    user = token_info[1]
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO
                       questions(competition_fk, created_by_fk, question_data, answer_data)
                       VALUES
                       ((SELECT id FROM competitions WHERE name=%s),
                       (SELECT id FROM users WHERE username=%s),
                       %s,
                       %s)
                       """, (comp_name, user, question_data, answer_data))
        conn.commit()
    return json.dumps({'success': True})

def get_competition_list(token):
    if get_token_info(token)[2] != 'admin':
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    with conn.cursor() as cur:
        cur.execute("""SELECT c.name, ct.description FROM
                       competitions AS c INNER JOIN
                       competition_types AS ct
                       ON c.type_fk=ct.id
                       ORDER BY c.id
                       """)
        return json.dumps(cur.fetchall())

def remove_question(token, competition, question):
    if get_token_info(token)[2] != 'admin':
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM questions
                       WHERE
                       competition_fk=
                       (SELECT id FROM competitions WHERE name=%s)
                       AND
                       question_data=%s
                       """, (competition, question))
        if cur.rowcount == 0:
            return json.dumps({'success': False, 'reason': 'Invalid question'})
        conn.commit()
    return json.dumps({'success': True})

def competition_exists(competition):
    with conn.cursor() as cur:
        cur.execute("""SELECT COUNT(*)
                       FROM competitions
                       WHERE name=%s
                       """, (competition,))
        return int(cur.fetchone()[0]) == 1

def add_competitor(token, competition, user):
    token_info = get_token_info(token)
    if token_info[2] != 'admin':
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    if not user_exists(token_info[1]):
        return json.dumps({'success': False, 'reason': 'Invalid user'})
    if not competition_exists(competition):
        return json.dumps({'success': False, 'reason': 'Invalid competition'})
    with conn.cursor() as cur:
        try:
            cur.execute("""INSERT INTO
                           participations(competition_fk, user_fk)
                           VALUES
                           ((SELECT id FROM competitions WHERE name=%s),
                           (SELECT id FROM users WHERE username=%s))
                           """, (competition, user))
            conn.commit()
        except:
            return json.dumps({'success': False, 'reason': 'User already added'})
    return json.dumps({'success': True})

def is_participant(competition, user):
    with conn.cursor() as cur:
        cur.execute("""SELECT COUNT(id)
                       FROM
                       participations
                       WHERE
                       user_fk=(SELECT id FROM users WHERE username=%s)
                       AND
                       competition_fk=(SELECT id FROM competitions WHERE name=%s)
                       """, (user, competition))
        return cur.rowcount == 1

def get_competition_questions(token, competition):
    token_info = get_token_info(token)
    if token_info[2] == 'admin':
        with conn.cursor() as cur:
            cur.execute("""SELECT q.question_data, q.answer_data, ct.description
                           FROM questions AS q
                           INNER JOIN competitions AS c
                           ON q.competition_fk=c.id
                           INNER JOIN competition_types AS ct
                           ON c.type_fk=ct.id
                           WHERE c.name=%s
                           ORDER BY q.id
                           """, (competition,))
            if cur.rowcount == 0:
                return json.dumps({})
            result_list = [{'question_data': (row[0] if row[2] in ('fill', 'code') else json.loads(row[0])),\
                            'answer_data': row[1]} for row in cur.fetchall()]
            return json.dumps(result_list)
    elif token_info[2] == 'user':
        if not is_participant(competition, token_info[1]):
            return json.dumps({'success': False, 'reason': 'User not participating'})
        with conn.cursor() as cur:
            cur.execute("""SELECT q.question_data, ct.description
                           FROM questions AS q
                           INNER JOIN competitions AS c
                           ON q.competition_fk=c.id
                           INNER JOIN competition_types AS ct
                           ON c.type_fk=ct.id
                           WHERE c.name=%s
                           ORDER BY q.id
                           """, (competition,))
            if cur.rowcount == 0:
                return json.dumps({})
            result_list = [{'question_data': (row[0] if row[2] in ('fill', 'code') else json.loads(row[0]))}\
                          for row in cur.fetchall()]
            return json.dumps(result_list)
    else:
        return json.dumps({'success': False, 'reason': 'Invalid token'})

def submit_answer(token, comp_name, question, answer):
    token_info = get_token_info(token)
    if not token_info[0]:
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    username = token_info[1]
    if not is_participant(comp_name, username):
        return json.dumps({'success': False, 'reason': 'User not participating'})
    with conn.cursor() as cur:
        cur.execute("""REPLACE INTO
                       answers(user_fk, question_fk, answer)
                       VALUES
                       ((SELECT id FROM users WHERE username=%s),
                       (SELECT id FROM questions WHERE question_data=%s),
                       %s)
                       """, (username, question_data, answer))
        conn.commit()
        if cur.rowcount == 0:
            return {'success': False}
        else:
            return {'success': True}

def get_competition_type(comp_name):
    with conn.cursor() as cur:
        cur.execute("""SELECT ct.description
                       FROM
                       competitions AS c
                       INNER JOIN
                       competition_types AS ct
                       ON c.type_fk=ct.id
                       WHERE c.name=%s
                       """, (comp_name,))
        return cur.fetchone()[0]

def add_task_file(token, competition, task_name, file_data, filename):
    token_info = get_token_info(token)
    if token_info[2] != 'admin':
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    if get_competition_type(competition) != 'code':
        return json.dumps({'success': False, 'reason': 'Invalid competition'})
    user = token_info[1]
    filename = secure_filename(filename)
    filepath = upload_folder + '/' + filename
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO
                       tasks(competition_fk, name, filepath, added_by_fk)
                       VALUES
                       ((SELECT id FROM competitions WHERE name=%s),
                       %s,
                       %s,
                       (SELECT id FROM users WHERE username=%s))
                       """, (competition, task_name, filename, user))
        if cur.rowcount == 1:
            conn.commit()
            with open(filepath, 'wb') as fout:
                fout.write(file_data.encode('ascii'))
            return json.dumps({'success': True})
        else:
            return json.dumps({'success': False})

def download_task_file(token, competition, task_name):
    token_info = get_token_info(token)
    if token_info[2] not in ('admin', 'user'):
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    with conn.cursor() as cur:
        cur.execute("""SELECT filepath
                       FROM tasks
                       WHERE
                       competition_fk=
                       (SELECT id FROM competitions WHERE name=%s)
                       AND
                       name=%s
                       """, (competition, task_name))
        result = cur.fetchone()
        if result is None:
            return json.dumps({'success': False, 'reason': 'Invalid competition or task name'})
        filepath = result[0]
        return send_from_directory('static/task_files', filepath)

def get_task_list(token, comp_name):
    token_info = get_token_info(token)
    if token_info[0] is False:
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    elif token_info[2] == 'admin' or is_participant(token_info[1]):
        with conn.cursor() as cur:
            cur.execute("""SELECT name
                           FROM tasks
                           WHERE
                           competition_fk=
                           (SELECT id FROM competitions WHERE name=%s)
                           """, (comp_name,))
            result = [row[0] for row in cur.fetchall()]
            return json.dumps(result)

def get_competition_results(token, competition):
    token_info = get_token_info(token)
    if not token_info[0]:
        return json.dumps({'success': False, 'reason': 'Invalid token'})
    with conn.cursor() as cur:
        cur.execute("""SELECT u.username, CAST(SUM(a.points) AS SIGNED) AS p
                       FROM
                       users AS u
                       INNER JOIN
                       answers AS a
                       ON
                       u.id=a.user_fk
                       INNER JOIN
                       questions AS q
                       ON
                       a.question_fk=q.id
                       INNER JOIN
                       competitions AS c
                       ON
                       q.competition_fk=c.id
                       WHERE
                       c.name=%s
                       GROUP BY
                       u.username
                       ORDER BY p DESC
                       """, (competition,))
        results = [(row[0], row[1]) for row in cur.fetchall()]
        return json.dumps(results)
