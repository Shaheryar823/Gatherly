from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.db import get_db_connection

social_bp = Blueprint('social', __name__)

# Create a new post
@social_bp.route('/posts/create', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash("You must be logged in to post.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        content = request.form['content']
        user_id = session['user_id']

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO posts (user_id, content) VALUES (%s, %s)",
                (user_id, content)
            )
            conn.commit()
            flash("Post created successfully!", "success")
            return redirect(url_for('social.view_posts'))
        except Exception as e:
            conn.rollback()
            flash("Error creating post.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template('post_create.html')

# View all posts (feed)
@social_bp.route('/posts')
def view_posts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT posts.id, users.username, posts.content, posts.created_at
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
    posts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('post_list.html', posts=posts)

# Edit Post
@social_bp.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE id=%s AND user_id=%s", (post_id, session['user_id']))
    post = cur.fetchone()

    if not post:
        flash("Post not found or unauthorized.", "danger")
        cur.close()
        conn.close()
        return redirect(url_for('social.view_posts'))

    if request.method == 'POST':
        content = request.form['content']
        try:
            cur.execute("UPDATE posts SET content=%s WHERE id=%s", (content, post_id))
            conn.commit()
            flash("Post updated successfully!", "success")
            return redirect(url_for('social.view_posts'))
        except:
            conn.rollback()
            flash("Error updating post.", "danger")
    cur.close()
    conn.close()

    return render_template('post_create.html', post=post)

# Delete Post
@social_bp.route('/posts/delete/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM posts WHERE id=%s AND user_id=%s", (post_id, session['user_id']))
        conn.commit()
        flash("Post deleted successfully!", "success")
    except:
        conn.rollback()
        flash("Error deleting post.", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('social.view_posts'))
