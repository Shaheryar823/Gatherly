from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user_model import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash("You're already logged in.", "info")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.create(username, email, password):
            flash("Account created successfully!", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Error: Email or username already exists.", "danger")

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash("You're already logged in.", "info")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.get_by_email(email)
        if user and User.verify_password(user, password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.home'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))
