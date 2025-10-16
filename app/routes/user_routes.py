from flask import Blueprint, render_template, abort, session, flash, redirect, url_for
from app.models.user_model import User
from app.models.post_model import PostModel
from app.models.event_model import Event

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile/<int:user_id>')
def profile(user_id):
    # Fetch user info
    user = User.get_by_id(user_id)
    if not user:
        abort(404)  # Handle invalid user ID

    # Optionally require login (depends on your app policy)
    # If you want public profiles, remove this check:
    if 'user_id' not in session:
        flash("Please log in to view profiles.", "warning")
        return redirect(url_for('auth.login'))

    # Optional: Save some data in session (only if needed)
    # session['email'] = user['email']  # safer if using dict instead of tuple

    # Fetch data for user's posts and events
    posts = PostModel.get_by_user(user_id)
    events = Event.get_by_user(user_id)

    return render_template('profile.html', user=user, posts=posts, events=events)
