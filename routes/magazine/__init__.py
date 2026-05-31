# routes/magazine/__init__.py
from flask import Blueprint

magazine_bp = Blueprint(
    'magazine',
    __name__,
    template_folder='../../templates/magazine',
    static_folder='../../static',
    url_prefix='/magazine'
)

# Import routes after blueprint creation to avoid circular imports
from . import routes
