from .user import user_views
from .index import index_views
from .auth import auth_views
from .shift import shift_views          
from .attendance import attendance_views  
from .report import report_views
from .admin import setup_admin     
from flask import Flask

_all_blueprints = [
    user_views,
    index_views,
    auth_views,
    shift_views,
    attendance_views,
    report_views,
]


views = _all_blueprints

__all__ = [
    'user_views', 'index_views', 'auth_views', 'shift_views',
    'attendance_views', 'report_views', 'setup_admin', 'views', 'register_views'
]

def register_views(app):
  
    app.config.setdefault('SECRET_KEY', 'your_secret_key')
    for bp in _all_blueprints:
        app.register_blueprint(bp)
 
