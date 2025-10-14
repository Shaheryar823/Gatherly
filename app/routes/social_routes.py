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

    # Fetch posts
    cur.execute("""
        SELECT posts.id, users.username, posts.content, posts.created_at
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
    posts = cur.fetchall()

    full_posts = []
    for post in posts:
        post_id = post[0]

        # Fetch comments
        cur.execute("""
            SELECT users.username, comments.content
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at ASC
        """, (post_id,))
        comments = cur.fetchall()

        # Count likes
        cur.execute("SELECT COUNT(*) FROM likes WHERE post_id=%s", (post_id,))
        likes_count = cur.fetchone()[0]

        full_posts.append((*post, comments, likes_count))

    cur.close()
    conn.close()

    return render_template('post_list.html', posts=full_posts)


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


# ----------------------------
# 💬 Comments
# ----------------------------
@social_bp.route('/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash("Login to comment.", "danger")
        return redirect(url_for('auth.login'))

    content = request.form.get('comment')
    if not content.strip():
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for('social.view_posts'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s)",
        (session['user_id'], post_id, content)
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Comment added!", "success")
    return redirect(url_for('social.view_posts'))


# ----------------------------
# ❤️ Likes
# ----------------------------
@social_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    if 'user_id' not in session:
        flash("Login to like posts.", "danger")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if already liked
    cur.execute("SELECT id FROM likes WHERE user_id=%s AND post_id=%s", (user_id, post_id))
    like = cur.fetchone()

    if like:
        cur.execute("DELETE FROM likes WHERE id=%s", (like[0],))
    else:
        cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('social.view_posts'))

from flask import jsonify

# AJAX: Like/Unlike post
@social_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
def api_toggle_like(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in or register to like posts.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM likes WHERE user_id=%s AND post_id=%s", (user_id, post_id))
    like = cur.fetchone()

    if like:
        cur.execute("DELETE FROM likes WHERE id=%s", (like[0],))
        conn.commit()
        liked = False
    else:
        cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))
        conn.commit()
        liked = True

    cur.execute("SELECT COUNT(*) FROM likes WHERE post_id=%s", (post_id,))
    like_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({'liked': liked, 'likes': like_count})



# AJAX: Add comment
@social_bp.route('/api/posts/<int:post_id>/comment', methods=['POST'])
def api_add_comment(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in or register to comment.'}), 401

    data = request.get_json()
    content = data.get('comment', '').strip()
    if not content:
        return jsonify({'error': 'Empty comment'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s) RETURNING id",
        (session['user_id'], post_id, content)
    )
    conn.commit()

    # Fetch username to display instantly
    cur.execute("SELECT username FROM users WHERE id=%s", (session['user_id'],))
    username = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({'username': username, 'content': content})
