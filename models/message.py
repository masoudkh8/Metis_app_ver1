# models/message.py
from . import db
from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rfq_proposal_id = db.Column(db.Integer, db.ForeignKey('rfq_proposals.id'), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    is_read = db.Column(db.Boolean, default=False)

    # رابطه‌ها
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    rfq_proposal_rel = db.relationship('RFQProposal', foreign_keys=[rfq_proposal_id], backref='proposal_messages_list')

    def __repr__(self):
        return f"<Message from {self.sender.username} to {self.receiver.username}>"