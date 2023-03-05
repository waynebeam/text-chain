import psycopg2
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

# with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
#     with conn.cursor() as cur:
        
def create_new_user_in_db(new_username, new_password, new_email):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            name_check_sql = 'SELECT COUNT(username) FROM users WHERE username = %s'
            email_check_sql = 'SELECT COUNT(email) FROM users WHERE email = %s'
            cur.execute(email_check_sql, (new_email,))
            if cur.fetchone()[0] != 0:
                return False
            cur.execute(name_check_sql, (new_username,))
            if cur.fetchone()[0] != 0:
                return False
        
            create_new_user_sql = 'INSERT INTO users(username, email, password_hash, date_created) VALUES(%s, %s, %s, %s)'
            password_hash = create_new_hash(new_password)
            new_user_data = (new_username,new_email, password_hash, 'NOW()')
            cur.execute(create_new_user_sql, new_user_data)

            return True


def login_against_db(submitted_username, submitted_password):
    password_hash = create_new_hash(submitted_password)

    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            login_validation_sql = 'SELECT username, email, id FROM users WHERE username = %s AND password_hash = %s'
            data = (submitted_username, password_hash)
            cur.execute(login_validation_sql, data)
            result = cur.fetchone()
            if result:
                return result
            return False

def find_threads_for_user(user_id):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = 'SELECT DISTINCT ON(thread_id) text FROM messages WHERE user_id = %s'
            cur.execute(sql,user_id)
            result = cur.fetchall()
            if result:
                return result
            return None

def create_new_hash(original_string):
    return hashlib.sha256(original_string.encode("UTF-8")).hexdigest()


def test_db_access():
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = "INSERT INTO users(username, password_hash, email) VALUES(%s, %s, %s) RETURNING (id)"
            data = ("test", "test again", "test")
            cur.execute(sql,data)
            print(cur.fetchone())

