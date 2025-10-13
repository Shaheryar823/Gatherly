from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.utils.db import get_db_connection


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch posts
    cur.execute("""
        SELECT p.id, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
    """)
    posts = [
        {
            "id": row[0],
            "title": "Post",
            "content": row[1],
            "created_at": row[2],
            "author": row[3],
            "type": "post"
        }
        for row in cur.fetchall()
    ]

    # Fetch events
    cur.execute("""
        SELECT e.id, e.title, e.description, e.event_date, e.created_at, u.username
        FROM events e
        JOIN users u ON e.user_id = u.id
    """)
    events = [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "date": row[3],
            "created_at": row[4],
            "author": row[5],
            "type": "event"
        }
        for row in cur.fetchall()
    ]

    conn.close()

    # Combine and sort by creation date (descending)
    feed = sorted(posts + events, key=lambda x: x["created_at"], reverse=True)

    return render_template("index.html", feed=feed, session=session)


@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You must be logged in to access the dashboard.", "danger")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch user events
    cur.execute("SELECT * FROM events WHERE user_id=%s ORDER BY event_date ASC", (user_id,))
    events = cur.fetchall()

    # Fetch user posts
    cur.execute("SELECT * FROM posts WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    posts = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('dashboard.html', events=events, posts=posts)
