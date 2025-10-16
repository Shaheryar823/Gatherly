from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_db_connection

class User:

    @staticmethod
    def create(username, email, password):
        hashed = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, hashed)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username,  email FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user

    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user[2], password)
