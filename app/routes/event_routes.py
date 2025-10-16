from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.event_model import Event

event_bp = Blueprint('event', __name__)

@event_bp.route('/events/create', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        flash("You must be logged in to create an event.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        success = Event.create(
            user_id=session['user_id'],
            title=request.form['title'],
            description=request.form['description'],
            event_date=request.form['event_date'],
            location=request.form['location']
        )

        if success:
            flash("Event created successfully!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Error creating event.", "danger")

    return render_template('event_create.html')


@event_bp.route('/events')
def list_events():
    events = Event.get_all()
    return render_template('event_list.html', events=events)


@event_bp.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('auth.login'))

    event = Event.get_by_id(event_id, session['user_id'])
    if not event:
        flash("Event not found or unauthorized.", "danger")
        return redirect(url_for('event.list_events'))

    if request.method == 'POST':
        success = Event.update(
            event_id=event_id,
            title=request.form['title'],
            description=request.form['description'],
            event_date=request.form['event_date'],
            location=request.form['location']
        )

        if success:
            flash("Event updated successfully!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Error updating event.", "danger")

    return render_template('event_create.html', event=event)


@event_bp.route('/events/delete/<int:event_id>')
def delete_event(event_id):
    if 'user_id' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('auth.login'))

    success = Event.delete(event_id, session['user_id'])
    if success:
        flash("Event deleted successfully!", "success")
    else:
        flash("Error deleting event.", "danger")

    return redirect(url_for('main.dashboard'))
