from flask import Blueprint, render_template, session, redirect, url_for, flash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Homepage only shows category boxes (no data needed yet)
    return render_template("index.html", session=session)


@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You must be logged in to access the dashboard.", "danger")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # Fetch data for user's posts and events
    from app.models.post_model import PostModel
    from app.models.event_model import Event

    posts = PostModel.get_by_user(user_id)
    events = Event.get_by_user(user_id)

    return render_template('dashboard.html', events=events, posts=posts)
