from app.utils.db import get_db_connection

class Event:
    @staticmethod
    def create(user_id, title, description, event_date, location):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO events (user_id, title, description, event_date, location)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, title, description, event_date, location)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print("Error creating event:", e)
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, description, event_date, location FROM events ORDER BY event_date ASC")
        events = cur.fetchall()
        cur.close()
        conn.close()
        return events

    @staticmethod
    def get_by_id(event_id, user_id=None):
        conn = get_db_connection()
        cur = conn.cursor()
        if user_id:
            cur.execute("SELECT * FROM events WHERE id=%s AND user_id=%s", (event_id, user_id))
        else:
            cur.execute("SELECT * FROM events WHERE id=%s", (event_id,))
        event = cur.fetchone()
        cur.close()
        conn.close()
        return event
    
    @staticmethod
    def get_by_user(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM events WHERE user_id=%s ORDER BY event_date ASC", (user_id,))
        events = cur.fetchall()
        cur.close()
        conn.close()
        return events

    @staticmethod
    def update(event_id, title, description, event_date, location):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE events
                SET title=%s, description=%s, event_date=%s, location=%s
                WHERE id=%s
                """,
                (title, description, event_date, location, event_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print("Error updating event:", e)
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete(event_id, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM events WHERE id=%s AND user_id=%s", (event_id, user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print("Error deleting event:", e)
            return False
        finally:
            cur.close()
            conn.close()
