from email.policy import default
from utils import db
from datetime import datetime

class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(20), index=True, unique=True)
    password = db.Column(db.String(20))
    role = db.Column(db.String(20))
    create_dt = db.Column(db.DateTime, default=datetime.now)


class Question(db.Model):
    __tablename__='question'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    question = db.Column(db.String(500), unique=True)
    option1 = db.Column(db.String(200))
    option2 = db.Column(db.String(200))
    option3 = db.Column(db.String(200))
    option4 = db.Column(db.String(200))
    answer = db.Column(db.String(10))
    explain = db.Column(db.Text)
    status = db.Column(db.Boolean, default=True)
    create_dt = db.Column(db.DateTime, default=datetime.now)

class Assessment(db.Model):
    __tablename__='assessment'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title =  db.Column(db.String(200))
    question_ids = db.Column(db.String(100))
    category =  db.Column(db.String(20)) # Formative (multiple times), Summative (only  once)
    duration_time = db.Column(db.Integer, default= 40)
    due_time = db.Column(db.String(20))
    activate = db.Column(db.Boolean, default=True)
    create_dt = db.Column(db.DateTime, default=datetime.now)

class History(db.Model):
    __tablename__='history'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    assessment_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    question_ids = db.Column(db.String(100))
    student_name = db.Column(db.String(20))
    replys = db.Column(db.String(30))
    times = db.Column(db.Integer)
    duration_time = db.Column(db.Integer)
    score = db.Column(db.Integer)
    category =  db.Column(db.String(20))
    create_dt = db.Column(db.DateTime, default=datetime.now)