"""
Exhibition Services - Virtual Booth Management and Interaction Logic
Handles booth visits, interactions, appointments, and gamification.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import current_app

from models import db, User
from models.exhibition_trading_models import (
    Exhibition, Booth, BoothVisit, BoothInteraction, 
    BoothAppointment, ExhibitionVisit, BoothType, ExhibitionStatus
)


class ExhibitionService:
    """Service layer for exhibition management."""
    
    @staticmethod
    def get_active_exhibitions(limit: int = 10) -> List[Exhibition]:
        """Get all active exhibitions."""
        return Exhibition.query.filter_by(
            status=ExhibitionStatus.ACTIVE
        ).order_by(Exhibition.start_date.desc()).limit(limit).all()
    
    @staticmethod
    def get_upcoming_exhibitions(limit: int = 10) -> List[Exhibition]:
        """Get upcoming exhibitions."""
        now = datetime.utcnow()
        return Exhibition.query.filter(
            Exhibition.status == ExhibitionStatus.ACTIVE,
            Exhibition.start_date > now
        ).order_by(Exhibition.start_date.asc()).limit(limit).all()
    
    @staticmethod
    def get_exhibition_details(exhibition_id: str) -> Optional[Exhibition]:
        """Get detailed information about an exhibition."""
        return db.session.get(Exhibition, exhibition_id)
    
    @staticmethod
    def record_exhibition_visit(exhibition_id: str, user_id: str) -> Optional[ExhibitionVisit]:
        """Record a user's visit to an exhibition."""
        try:
            # Check if already visited today
            today = datetime.utcnow().date()
            existing_visit = ExhibitionVisit.query.filter(
                ExhibitionVisit.exhibition_id == exhibition_id,
                ExhibitionVisit.user_id == user_id,
                db.func.date(ExhibitionVisit.visited_at) == today
            ).first()
            
            if existing_visit:
                return existing_visit
            
            visit = ExhibitionVisit(
                id=uuid.uuid4(),
                exhibition_id=exhibition_id,
                user_id=user_id,
                visited_at=datetime.utcnow(),
                duration_seconds=0,
                pages_viewed=1
            )
            
            db.session.add(visit)
            db.session.commit()
            
            return visit
            
        except Exception as e:
            current_app.logger.error(f"Error recording exhibition visit: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_exhibition_stats(exhibition_id: str) -> dict:
        """Get statistics for an exhibition."""
        exhibition = db.session.get(Exhibition, exhibition_id)
        if not exhibition:
            return {}
        
        total_booths = Booth.query.filter_by(exhibition_id=exhibition_id).count()
        total_visits = ExhibitionVisit.query.filter_by(exhibition_id=exhibition_id).count()
        unique_visitors = db.session.query(
            db.func.count(db.distinct(ExhibitionVisit.user_id))
        ).filter_by(exhibition_id=exhibition_id).scalar()
        
        return {
            'total_booths': total_booths,
            'total_visits': total_visits,
            'unique_visitors': unique_visitors or 0,
            'status': exhibition.status.value,
            'start_date': exhibition.start_date.isoformat(),
            'end_date': exhibition.end_date.isoformat() if exhibition.end_date else None
        }


class BoothService:
    """Service layer for booth management and interactions."""
    
    @staticmethod
    def get_booths_by_exhibition(exhibition_id: str, booth_type: Optional[str] = None) -> List[Booth]:
        """Get all booths for an exhibition, optionally filtered by type."""
        query = Booth.query.filter_by(exhibition_id=exhibition_id)
        if booth_type:
            query = query.filter_by(booth_type=booth_type)
        return query.order_by(Booth.created_at.desc()).all()
    
    @staticmethod
    def get_booth_details(booth_id: str) -> Optional[Booth]:
        """Get detailed information about a booth."""
        return db.session.get(Booth, booth_id)
    
    @staticmethod
    def record_booth_visit(booth_id: str, user_id: str, duration_seconds: int = 0) -> Optional[BoothVisit]:
        """Record a user's visit to a booth."""
        try:
            booth = db.session.get(Booth, booth_id)
            if not booth:
                return None
            
            visit = BoothVisit(
                id=uuid.uuid4(),
                booth_id=booth_id,
                user_id=user_id,
                visited_at=datetime.utcnow(),
                duration_seconds=duration_seconds,
                interaction_score=0
            )
            
            db.session.add(visit)
            
            # Update booth visit count
            booth.total_visits = (booth.total_visits or 0) + 1
            booth.unique_visitors = db.session.query(
                db.func.count(db.distinct(BoothVisit.user_id))
            ).filter_by(booth_id=booth_id).scalar() or 0
            
            db.session.commit()
            return visit
            
        except Exception as e:
            current_app.logger.error(f"Error recording booth visit: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def record_interaction(booth_id: str, user_id: str, interaction_type: str, 
                          content: Optional[str] = None) -> Optional[BoothInteraction]:
        """Record a user interaction with a booth."""
        try:
            interaction = BoothInteraction(
                id=uuid.uuid4(),
                booth_id=booth_id,
                user_id=user_id,
                interaction_type=interaction_type,
                content=content,
                created_at=datetime.utcnow()
            )
            
            db.session.add(interaction)
            
            # Update booth interaction count
            booth = db.session.get(Booth, booth_id)
            if booth:
                booth.total_interactions = (booth.total_interactions or 0) + 1
                db.session.commit()
            
            return interaction
            
        except Exception as e:
            current_app.logger.error(f"Error recording interaction: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def create_appointment(booth_id: str, user_id: str, scheduled_time: datetime,
                          topic: str, notes: Optional[str] = None) -> Optional[BoothAppointment]:
        """Create an appointment with a booth owner."""
        try:
            booth = db.session.get(Booth, booth_id)
            if not booth:
                return None
            
            # Check for conflicts
            existing = BoothAppointment.query.filter(
                BoothAppointment.booth_id == booth_id,
                BoothAppointment.scheduled_time == scheduled_time,
                BoothAppointment.status.in_(['pending', 'confirmed'])
            ).first()
            
            if existing:
                return None
            
            appointment = BoothAppointment(
                id=uuid.uuid4(),
                booth_id=booth_id,
                user_id=user_id,
                owner_id=booth.owner_user_id,
                scheduled_time=scheduled_time,
                duration_minutes=30,
                topic=topic,
                notes=notes,
                status='pending'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            return appointment
            
        except Exception as e:
            current_app.logger.error(f"Error creating appointment: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_user_appointments(user_id: str, status: Optional[str] = None) -> List[BoothAppointment]:
        """Get all appointments for a user."""
        query = BoothAppointment.query.filter(
            db.or_(
                BoothAppointment.user_id == user_id,
                BoothAppointment.owner_id == user_id
            )
        )
        if status:
            query = query.filter_by(status=status)
        return query.order_by(BoothAppointment.scheduled_time.desc()).all()
    
    @staticmethod
    def update_appointment_status(appointment_id: str, status: str) -> bool:
        """Update appointment status."""
        appointment = db.session.get(BoothAppointment, appointment_id)
        if not appointment:
            return False
        
        appointment.status = status
        db.session.commit()
        return True
    
    @staticmethod
    def get_booth_stats(booth_id: str) -> dict:
        """Get statistics for a booth."""
        booth = db.session.get(Booth, booth_id)
        if not booth:
            return {}
        
        total_visits = BoothVisit.query.filter_by(booth_id=booth_id).count()
        unique_visitors = db.session.query(
            db.func.count(db.distinct(BoothVisit.user_id))
        ).filter_by(booth_id=booth_id).scalar() or 0
        
        total_interactions = BoothInteraction.query.filter_by(booth_id=booth_id).count()
        pending_appointments = BoothAppointment.query.filter_by(
            booth_id=booth_id, status='pending'
        ).count()
        
        return {
            'total_visits': total_visits,
            'unique_visitors': unique_visitors,
            'total_interactions': total_interactions,
            'pending_appointments': pending_appointments,
            'booth_type': booth.booth_type.value,
            'is_featured': booth.is_featured
        }


class GamificationService:
    """Service layer for exhibition gamification."""
    
    @staticmethod
    def calculate_visitor_level(user_id: str) -> dict:
        """Calculate visitor level based on activity."""
        total_visits = BoothVisit.query.filter_by(user_id=user_id).count()
        total_interactions = BoothInteraction.query.filter_by(user_id=user_id).count()
        total_appointments = BoothAppointment.query.filter(
            db.or_(
                BoothAppointment.user_id == user_id,
                BoothAppointment.owner_id == user_id
            )
        ).count()
        
        # Simple leveling algorithm
        score = total_visits * 10 + total_interactions * 20 + total_appointments * 50
        
        if score >= 1000:
            level = "Platinum Visitor"
        elif score >= 500:
            level = "Gold Visitor"
        elif score >= 200:
            level = "Silver Visitor"
        elif score >= 50:
            level = "Bronze Visitor"
        else:
            level = "Newcomer"
        
        return {
            'level': level,
            'score': score,
            'total_visits': total_visits,
            'total_interactions': total_interactions,
            'total_appointments': total_appointments
        }
    
    @staticmethod
    def get_recent_activity(user_id: str, limit: int = 10) -> List[dict]:
        """Get recent activity for a user."""
        activities = []
        
        # Recent booth visits
        visits = BoothVisit.query.filter_by(user_id=user_id).order_by(
            BoothVisit.visited_at.desc()
        ).limit(limit).all()
        
        for visit in visits:
            booth = db.session.get(Booth, visit.booth_id)
            activities.append({
                'type': 'booth_visit',
                'timestamp': visit.visited_at.isoformat(),
                'details': {
                    'booth_name': booth.name_en if booth else 'Unknown',
                    'duration': visit.duration_seconds
                }
            })
        
        # Recent interactions
        interactions = BoothInteraction.query.filter_by(user_id=user_id).order_by(
            BoothInteraction.created_at.desc()
        ).limit(limit).all()
        
        for interaction in interactions:
            booth = db.session.get(Booth, interaction.booth_id)
            activities.append({
                'type': f'interaction_{interaction.interaction_type}',
                'timestamp': interaction.created_at.isoformat(),
                'details': {
                    'booth_name': booth.name_en if booth else 'Unknown'
                }
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return activities[:limit]


# Service instances
exhibition_service = ExhibitionService()
booth_service = BoothService()
gamification_service = GamificationService()
