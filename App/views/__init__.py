from .user import user_views
from .index import index_views
from .auth import auth_views
from .shift import shift_views          
from .attendance import attendance_views  
from .report import report_views
from .admin import setup_admin     

from App.database import init_db
from flask import Flask     
from App.views import views

_all_blueprints = [
    user_views,
    index_views,
    auth_views,
    shift_views,
    attendance_views,
    report_views,
]

def register_views(app):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    init_db(app) 
        
    for bp in views:
        app.register_blueprint(bp)

    setup_admin(app)   
