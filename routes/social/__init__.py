# routes/social/__init__.py
from flask import Blueprint

social_bp = Blueprint('social', __name__, url_prefix='/social')

# Import routes after creating blueprint to avoid circular imports
from . import routes
