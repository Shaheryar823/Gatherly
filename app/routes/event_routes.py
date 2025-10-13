from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.db import get_db_connection


event_bp = Blueprint('event', __name__)

# Create Event
@event_bp.route('/events/create', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        flash("You must be logged in to create an event.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        event_date = request.form['event_date']
        location = request.form['location']
        user_id = session['user_id']

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO events (user_id, title, description, event_date, location) VALUES (%s, %s, %s, %s, %s)",
                (user_id, title, description, event_date, location)
            )
            conn.commit()
            flash("Event created successfully!", "success")
            return redirect(url_for('event.list_events'))
        except Exception as e:
            conn.rollback()
            flash("Error creating event.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template('event_create.html')

# List Events (simple)
@event_bp.route('/events')
def list_events():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, event_date, location FROM events ORDER BY event_date ASC")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('event_list.html', events=events)

# Edit Event
@event_bp.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch event
    cur.execute("SELECT * FROM events WHERE id=%s AND user_id=%s", (event_id, session['user_id']))
    event = cur.fetchone()

    if not event:
        flash("Event not found or unauthorized.", "danger")
        cur.close()
        conn.close()
        return redirect(url_for('event.list_events'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        event_date = request.form['event_date']
        location = request.form['location']

        try:
            cur.execute("""
                UPDATE events
                SET title=%s, description=%s, event_date=%s, location=%s
                WHERE id=%s
            """, (title, description, event_date, location, event_id))
            conn.commit()
            flash("Event updated successfully!", "success")
            return redirect(url_for('event.list_events'))
        except:
            conn.rollback()
            flash("Error updating event.", "danger")
    cur.close()
    conn.close()

    return render_template('event_create.html', event=event)
    
# Delete Event
@event_bp.route('/events/delete/<int:event_id>')
def delete_event(event_id):
    if 'user_id' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM events WHERE id=%s AND user_id=%s", (event_id, session['user_id']))
        conn.commit()
        flash("Event deleted successfully!", "success")
    except:
        conn.rollback()
        flash("Error deleting event.", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('event.list_events'))
