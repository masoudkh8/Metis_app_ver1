from . import db
from sqlalchemy import UniqueConstraint, Index


class Port(db.Model):
    __tablename__ = 'ports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # ✅ ۱. جلوگیری از تکراری در سطح دیتابیس
    # ✅ ۲. ایندکس مختصات برای جستجوی شعاعی/جغرافیایی سریع‌تر
    __table_args__ = (
        UniqueConstraint('name', 'country', name='uq_port_name_country'),
        Index('idx_port_location', 'latitude', 'longitude'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'location': [self.latitude, self.longitude]
        }

    def __repr__(self):
        return f"<Port {self.name} ({self.country})>"