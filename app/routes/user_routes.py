from flask import Blueprint, render_template, session, redirect, url_for, flash, abort, request
from app.models.user_model import User
from app.models.post_model import PostModel
from app.models.event_model import Event

user_bp = Blueprint('user', __name__)

# 🧍 Profile Page
@user_bp.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.get_by_id(user_id)
    if not user:
        abort(404)

    # Redirect login if not logged in
    if 'user_id' not in session:
        flash("Please log in to view profiles.", "warning")
        return redirect(url_for('auth.login'))

    posts = PostModel.get_by_user(user_id)
    events = Event.get_by_user(user_id)

    # Fetch follow stats
    followers_count, following_count = User.get_follow_stats(user_id)
    followers = User.get_followers(user_id)
    following = User.get_following(user_id)

    # Check if current user already follows this profile
    current_user_id = session.get('user_id')
    is_following = any(f[0] == current_user_id for f in followers)

    return render_template(
        'profile.html',
        user=user,
        posts=posts,
        events=events,
        followers_count=followers_count,
        following_count=following_count,
        is_following=is_following
    )


# ➕ Follow user
@user_bp.route('/follow/<int:user_id>', methods=['POST'])
def follow(user_id):
    if 'user_id' not in session:
        flash("You must be logged in to follow users.", "danger")
        return redirect(url_for('auth.login'))

    follower_id = session['user_id']
    if follower_id == user_id:
        flash("You cannot follow yourself.", "warning")
        return redirect(url_for('user.profile', user_id=user_id))

    User.follow_user(follower_id, user_id)
    flash("You are now following this user!", "success")
    return redirect(url_for('user.profile', user_id=user_id))


# ➖ Unfollow user
@user_bp.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow(user_id):
    if 'user_id' not in session:
        flash("You must be logged in to unfollow users.", "danger")
        return redirect(url_for('auth.login'))

    follower_id = session['user_id']
    User.unfollow_user(follower_id, user_id)
    flash("You have unfollowed this user.", "info")
    return redirect(url_for('user.profile', user_id=user_id))
