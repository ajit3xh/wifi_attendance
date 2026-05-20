from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

def get_ist():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=get_ist)

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    host_ip = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_ist)
    host = db.relationship('User', backref=db.backref('hosted_meetings', lazy=True))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    method = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=get_ist)
    leave_date = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref=db.backref('attendances', lazy=True))
    meeting = db.relationship('Meeting', backref=db.backref('attendances', lazy=True))

class AttendanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=get_ist)
    attendance = db.relationship('Attendance', backref=db.backref('log', lazy=True))

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_ist)
    meeting = db.relationship('Meeting', backref=db.backref('polls', lazy=True))

class PollOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll = db.relationship('Poll', backref=db.backref('options', lazy=True))

class PollVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('poll_option.id'), nullable=False)
    poll = db.relationship('Poll', backref=db.backref('voted_users', lazy=True))
    user = db.relationship('User', backref=db.backref('votes', lazy=True))

class BannedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_ist)
