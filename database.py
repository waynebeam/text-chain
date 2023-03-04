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


def create_new_hash(original_string):
    return hashlib.sha256(original_string.encode("UTF-8")).hexdigest()

