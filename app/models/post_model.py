# app/models/post_model.py
from app.utils.db import get_db_connection


class PostModel:
    @staticmethod
    def create_post(user_id, content):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", (user_id, content))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print("Error creating post:", e)
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_posts():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT posts.id, users.username, posts.content, posts.created_at, posts.user_id
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
        """)
        posts = cur.fetchall()
        cur.close()
        conn.close()
        return posts

    @staticmethod
    def get_post_by_id(post_id, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM posts WHERE id=%s AND user_id=%s", (post_id, user_id))
        post = cur.fetchone()
        cur.close()
        conn.close()
        return post
    
    @staticmethod
    def get_by_user(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM posts WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
        posts = cur.fetchall()
        cur.close()
        conn.close()
        return posts

    @staticmethod
    def update_post(post_id, content):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE posts SET content=%s WHERE id=%s", (content, post_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print("Error updating post:", e)
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete_post(post_id, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM posts WHERE id=%s AND user_id=%s", (post_id, user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print("Error deleting post:", e)
            return False
        finally:
            cur.close()
            conn.close()
