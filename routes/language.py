#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Language Switcher Route for Metisma
Add this route to enable language switching functionality
"""

from flask import Blueprint, session, request, redirect, url_for
from functools import wraps

language_bp = Blueprint('language', __name__)


@language_bp.route('/set_language/<lang>')
def set_language(lang):
    """
    تغییر زبان کاربر / Set user language
    
    Args:
        lang: Language code ('fa_IR' or 'en')
    
    Returns:
        Redirect to previous page or home
    """
    supported_languages = ['fa_IR', 'en']
    
    if lang in supported_languages:
        session['lang'] = lang
        # Log language change (optional)
        print(f"Language changed to: {lang}")
    
    # Return to previous page or home
    return redirect(request.referrer or url_for('users.profile'))


def switch_language_decorator(lang):
    """
    دکوریتور برای تغییر زبان در view functions
    Decorator for changing language in view functions
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session['lang'] = lang
            return f(*args, **kwargs)
        return decorated_function
    return decorator
