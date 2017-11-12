import MySQLdb

import hashlib
import time
import random
import string

conn = MySQLdb.connect(host='localhost', user='admin', password='root', db='ETFOCS')
char_set = string.ascii_letters + string.digits + string.punctuation
#secret_key = ''.join([random.choice(char_set) for _ in range(64)])
secret_key = ''

def login(username, password):
    global conn
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM users WHERE username=%s AND password_hash=%s', (username, hashlib.sha256(password.encode('utf-8')).hexdigest()))
        result = cur.fetchone()
        if result is None:
            return None, False
        else:
            exp_at = str(int(time.time()) + 3600)
            token = username + '.' + exp_at
            token_hash = hashlib.sha256((token + secret_key).encode('utf-8')).hexdigest()
            return {'token': token, 'hash': token_hash}, True

def register(username, password):
    global conn
    with conn.cursor() as cur:
        cur.execute('INSERT INTO users(username, password_hash) VALUES (%s, %s)', (username, hashlib.sha256(password.encode('utf-8')).hexdigest()))
    conn.commit()
    return 'yos'

def user_exist(username):
    global conn
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM users WHERE username=%s', (username,))
        return cur.fetchone() is not None

def token_valid(token):
    token_string = token['token']
    token_hash = token['hash']
    if hashlib.sha256((token_string + secret_key).encode('utf-8')).hexdigest() != token_hash:
        return False
    user, exp_at = token_string.split('.')
    exp_at = int(exp_at)
    if not user_exists(user):
        return False
    return exp_at < time.time()
