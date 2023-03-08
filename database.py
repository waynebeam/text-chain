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
            sql = 'SELECT thread_id, length_viewed FROM user_thread_status WHERE user_id = %s'
            cur.execute(sql,user_id)
            threads = cur.fetchall()
            thread_ids = [t[0] for t in threads]
            viewed_lengths = [l[1] for l in threads]
            if thread_ids:
                start_of_thread_sql = "SELECT text, thread_id, user_id, next_user_id FROM messages WHERE thread_id = %s"
                result = []
                for i in range(len(thread_ids)):
                    cur.execute(start_of_thread_sql, [thread_ids[i]])
                    data = cur.fetchall()
                    thread_length = len(data)
                    next_user_id = data[-1][3]
                    last_writer_id = data[-1][2]
                    text_id_length = [data[0][0], data[0][1], viewed_lengths[i], thread_length, next_user_id, last_writer_id]
                    result.append(text_id_length)
                return result
            return None

def retrieve_entire_thread(thread_id):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = """
            SELECT messages.text, users.username, messages.next_user_id FROM messages
            JOIN users ON (messages.user_id = users.id)
            WHERE thread_id = %s
            """
            cur.execute(sql,[thread_id])
            return cur.fetchall()



def create_new_thread_on_db(user_id, text, next_user_id):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = "INSERT INTO messages(text, user_id, next_user_id) VALUES(%s, %s, %s) RETURNING id"
            data = (text,user_id, next_user_id)
            cur.execute(sql,data)
            new_thread_id = cur.fetchone()[0]
            set_thread_id_sql = "UPDATE messages SET thread_id = %s WHERE id = %s"
            cur.execute(set_thread_id_sql, (new_thread_id,new_thread_id))
            #TODO need to check here for null if user is wrong
            
            #TODO this will return false or true and the app route will have to adjust
            return new_thread_id
            

def get_id_from_username(username):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = "SELECT id FROM users WHERE username = %s"
            cur.execute(sql,(username,))
            id = cur.fetchone()
            if id:
                return id
            return False

def get_username_from_id(id):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = "SELECT username FROM users WHERE id=%s"
            cur.execute(sql, [id])
            return cur.fetchone()


def update_user_thread_status(user_id, thread_id, thread_length):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            find_row_sql = 'SELECT id FROM user_thread_status WHERE user_id = %s AND thread_id = %s'
            cur.execute(find_row_sql, [user_id, thread_id])
            row_id = cur.fetchone()
            if row_id:
                update_row_sql = 'UPDATE user_thread_status SET length_viewed = %s WHERE id = %s'
                cur.execute(update_row_sql, [thread_length, row_id])
                return
            insert_row_sql = 'INSERT INTO user_thread_status (user_id, thread_id, length_viewed) VALUES(%s, %s, %s)'
            cur.execute(insert_row_sql, [user_id,thread_id,0])

def add_message_to_thread(text,thread_id, user_id, next_user_id):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = 'INSERT INTO messages(text,user_id, thread_id, next_user_id) VALUES(%s, %s, %s, %s)'
            cur.execute(sql,[text, user_id,thread_id, next_user_id])

def get_last_message_id(thread_id):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = 'SELECT id FROM messages WHERE thread_id = %s'
            cur.execute(sql, [thread_id])
            id = cur.fetchall()
            return id[-1]

def update_message_text(text, id):
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = 'UPDATE messages SET text = %s WHERE id = %s'
            cur.execute(sql,[text, id])


def create_new_hash(original_string):
    return hashlib.sha256(original_string.encode("UTF-8")).hexdigest()


def test_db_access():
    with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
        with conn.cursor() as cur:
            sql = "INSERT INTO users(username, password_hash, email) VALUES(%s, %s, %s) RETURNING (id)"
            data = ("test", "test again", "test")
            cur.execute(sql,data)
            print(cur.fetchone())


# def access_db(func):
#     def wrapper(*args, **kwargs):
#         with psycopg2.connect(os.environ['DB_CONNECTION_STRING']) as conn:
#             with conn.cursor() as cur:
#                 value = func(*args, **kwargs)
#         return value
#     return wrapper