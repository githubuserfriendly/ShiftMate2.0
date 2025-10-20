from App.models import User
from App.database import db

def create_user(username, password, isAdmin=False):
    newuser = User(username=username, password=password, isAdmin=isAdmin)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user(id):
    return User.query.get(id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    return [user.get_json() for user in users] if users else []

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        db.session.commit()
        return user
    return None











