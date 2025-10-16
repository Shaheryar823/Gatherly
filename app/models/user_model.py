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


    # 🟢 Follow another user
    @staticmethod
    def follow_user(follower_id, followed_id):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO followers (follower_id, followed_id)
                VALUES (%s, %s)
                ON CONFLICT (follower_id, followed_id) DO NOTHING
            """, (follower_id, followed_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # 🔴 Unfollow a user
    @staticmethod
    def unfollow_user(follower_id, followed_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM followers
            WHERE follower_id = %s AND followed_id = %s
        """, (follower_id, followed_id))
        conn.commit()
        cur.close()
        conn.close()

    # 👥 Get followers (people who follow this user)
    @staticmethod
    def get_followers(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.username
            FROM followers f
            JOIN users u ON f.follower_id = u.id
            WHERE f.followed_id = %s
        """, (user_id,))
        followers = cur.fetchall()
        cur.close()
        conn.close()
        return followers

    # 👣 Get following (people this user follows)
    @staticmethod
    def get_following(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.username
            FROM followers f
            JOIN users u ON f.followed_id = u.id
            WHERE f.follower_id = %s
        """, (user_id,))
        following = cur.fetchall()
        cur.close()
        conn.close()
        return following

    # 📊 Get follower/following count
    @staticmethod
    def get_follow_stats(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM followers WHERE followed_id = %s", (user_id,))
        followers_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM followers WHERE follower_id = %s", (user_id,))
        following_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return followers_count, following_count
