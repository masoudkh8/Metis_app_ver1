# routes/users/__init__.py
from flask import Blueprint

users_bp = Blueprint(
    'users',
    __name__,
    template_folder='../../templates/users',
    static_folder='../../static',
    url_prefix='/users'
)
root_bp = Blueprint(
    'root',
    __name__,
    url_prefix='/'
)