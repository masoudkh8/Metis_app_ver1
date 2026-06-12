"""
Metisma Exhibition Routes - MVP Version
Interactive Booths, Virtual Tours, and Appointments
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import desc, func
import random
from flask_babel import gettext as _
from models.exhibition import Exhibition, Booth, BoothVisit, BoothInteraction, BoothAppointment, ExhibitionVisit
from models.user import User
from extensions import db

exhibition_bp = Blueprint('exhibition', __name__, url_prefix='/exhibition')

# --- Public Exhibition Hall ---

@exhibition_bp.route('/')
def hall():
    """Main Exhibition Hall - List of active exhibitions and featured booths"""
    # Get active exhibitions
    active_exhibitions = Exhibition.query.filter_by(status='active').order_by(desc(Exhibition.start_date)).all()
    
    # Get featured booths (random selection for variety)
    featured_booths = Booth.query.filter_by(is_featured=True, status='active').limit(8).all()
    
    # If no featured booths, get random active ones
    if not featured_booths:
        featured_booths = Booth.query.filter_by(status='active').order_by(func.random()).limit(8).all()
    
    stats = {
        'total_booths': Booth.query.filter_by(status='active').count(),
        'total_visitors': ExhibitionVisit.query.count(),
        'active_exhibitions': len(active_exhibitions)
    }
    
    return render_template('exhibition/hall.html', 
                         exhibitions=active_exhibitions, 
                         featured_booths=featured_booths,
                         stats=stats)

@exhibition_bp.route('/booth/<uuid:booth_id>')
def booth_detail(booth_id):
    """Individual Booth Page with Virtual Tour & Info"""
    booth = Booth.query.get_or_404(booth_id)
    
    # Track visit if user is logged in or via session (simplified for MVP)
    if current_user.is_authenticated:
        visit = BoothVisit(
            user_id=current_user.id,
            booth_id=booth.id,
            visit_duration=0  # Will be updated via JS later
        )
        db.session.add(visit)
        db.session.commit()
        
        # Add interaction point for visiting
        interaction = BoothInteraction(
            user_id=current_user.id,
            booth_id=booth.id,
            interaction_type='visit',
            points=5
        )
        db.session.add(interaction)
        db.session.commit()
    
    # Get upcoming appointments for this booth
    upcoming_slots = BoothAppointment.query.filter_by(
        booth_id=booth.id,
        status='scheduled'
    ).filter(
        BoothAppointment.appointment_time > datetime.now()
    ).order_by(BoothAppointment.appointment_time).limit(5).all()
    
    # Related booths in same exhibition
    related_booths = Booth.query.filter_by(
        exhibition_id=booth.exhibition_id,
        status='active'
    ).filter(Booth.id != booth.id).limit(4).all()
    
    return render_template('exhibition/booth_detail.html', 
                         booth=booth, 
                         upcoming_slots=upcoming_slots,
                         related_booths=related_booths)

@exhibition_bp.route('/booth/<uuid:booth_id>/appointment', methods=['POST'])
@login_required
def book_appointment(booth_id):
    """Book an appointment with booth owner"""
    booth = Booth.query.get_or_404(booth_id)
    
    data = request.form
    appointment_time_str = data.get('appointment_time')
    message = data.get('message', '')
    
    try:
        appointment_time = datetime.fromisoformat(appointment_time_str.replace('Z', '+00:00'))
    except:
        flash(_('Invalid time format.'), 'error')
        return redirect(url_for('exhibition.booth_detail', booth_id=booth_id))
    
    # Check availability (simple check for MVP)
    existing = BoothAppointment.query.filter_by(
        booth_id=booth_id,
        appointment_time=appointment_time,
        status='scheduled'
    ).first()
    
    if existing:
        flash(_('This time slot is already booked. Please choose another time.'), 'warning')
        return redirect(url_for('exhibition.booth_detail', booth_id=booth_id))
    
    appointment = BoothAppointment(
        booth_id=booth_id,
        user_id=current_user.id,
        host_id=booth.owner_id,  # Assuming owner_id exists
        appointment_time=appointment_time,
        message=message,
        status='scheduled'
    )
    
    db.session.add(appointment)
    
    # Award points for booking
    interaction = BoothInteraction(
        user_id=current_user.id,
        booth_id=booth_id,
        interaction_type='appointment_booked',
        points=20
    )
    db.session.add(interaction)
    
    db.session.commit()
    
    flash(_('Your appointment has been successfully booked!'), 'success')
    return redirect(url_for('exhibition.booth_detail', booth_id=booth_id))

@exhibition_bp.route('/booth/<uuid:booth_id>/interact', methods=['POST'])
@login_required
def interact_with_booth(booth_id):
    """API endpoint for interactions (like, share, save)"""
    data = request.json
    interaction_type = data.get('type', 'view')
    
    points_map = {
        'like': 10,
        'share': 15,
        'save': 10,
        'chat_start': 25
    }
    
    points = points_map.get(interaction_type, 5)
    
    interaction = BoothInteraction(
        user_id=current_user.id,
        booth_id=booth_id,
        interaction_type=interaction_type,
        points=points
    )
    db.session.add(interaction)
    db.session.commit()
    
    return jsonify({'success': True, 'points_earned': points})

@exhibition_bp.route('/my-visits')
@login_required
def my_visits():
    """User's visited booths history"""
    visits = BoothVisit.query.filter_by(user_id=current_user.id)\
        .order_by(desc(BoothVisit.visited_at)).all()
    appointments = BoothAppointment.query.filter_by(user_id=current_user.id)\
        .order_by(desc(BoothAppointment.created_at)).all()
    
    return render_template('exhibition/my_visits.html', visits=visits, appointments=appointments)

# --- Admin/Exhibitor Routes (Simplified) ---

@exhibition_bp.route('/manage/create-booth', methods=['GET', 'POST'])
@login_required
def create_booth():
    """Simple form to create a booth (for exhibitors)"""
    if request.method == 'POST':
        # Simplified creation for MVP
        title_fa = request.form.get('title_fa')
        description_fa = request.form.get('description_fa')
        exhibition_id = request.form.get('exhibition_id')
        
        # In real app, validate exhibition ownership etc.
        booth = Booth(
            title_fa=title_fa,
            description_fa=description_fa,
            exhibition_id=exhibition_id,
            owner_id=current_user.id,
            status='active',
            layout_config={'theme': 'modern', 'color': '#3b82f6'}
        )
        db.session.add(booth)
        db.session.commit()
        flash(_('Your booth has been created successfully!'), 'success')
        return redirect(url_for('exhibition.booth_detail', booth_id=booth.id))
    
    exhibitions = Exhibition.query.filter_by(status='active').all()
    return render_template('exhibition/create_booth.html', exhibitions=exhibitions)
