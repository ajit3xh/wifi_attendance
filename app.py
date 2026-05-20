import os
import jwt
import bcrypt
import qrcode
import io
import base64
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g
from dotenv import load_dotenv

from models import db, User, Meeting, Attendance, AttendanceLog, Poll, PollOption, PollVote, BannedUser, get_ist

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///attendance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'supersecretjwtkey_replace_in_prod')

db.init_app(app)

with app.app_context():
    db.create_all()

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt')
        if not token and 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.replace('Bearer ', '')
        
        if not token:
            if request.path.startswith('/api') or request.path.endswith('/api/data'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['userId'])
            if not current_user:
                raise Exception("User not found")
            g.user = current_user
        except Exception as e:
            if request.path.startswith('/api') or request.path.endswith('/api/data'):
                return jsonify({'error': 'Please authenticate.'}), 401
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_user():
    return dict(user=getattr(g, 'user', None))

@app.route('/')
def index():
    if request.cookies.get('jwt'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            error = 'Invalid user or password'
        else:
            token = jwt.encode({
                'userId': user.id,
                'exp': get_ist() + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie('jwt', token, httponly=True, max_age=24*60*60)
            return resp
            
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            error = 'Username exists or invalid'
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            
            token = jwt.encode({
                'userId': new_user.id,
                'exp': get_ist() + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie('jwt', token, httponly=True)
            return resp
            
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('jwt')
    return resp

@app.route('/dashboard')
@auth_required
def dashboard():
    hosted_meetings = Meeting.query.filter_by(host_id=g.user.id).order_by(Meeting.created_at.desc()).all()
    
    attendances_doc = Attendance.query.filter_by(user_id=g.user.id).order_by(Attendance.date.desc()).all()
    attended_history = []
    for a in attendances_doc:
        if a.meeting:
            attended_history.append({'meeting': a.meeting, 'attendanceId': a.id})
            
    message = request.args.get('message')
    error = request.args.get('error')
    client_ip = get_client_ip()
    
    return render_template('dashboard.html', 
        hostedMeetings=hosted_meetings, 
        attendedHistory=attended_history, 
        message=message, 
        error=error, 
        clientIp=client_ip
    )

@app.route('/meeting/create', methods=['POST'])
@auth_required
def create_meeting():
    title = request.form.get('title', 'Untitled Meeting')
    host_ip = get_client_ip()
    
    meeting = Meeting(title=title, host_id=g.user.id, host_ip=host_ip)
    db.session.add(meeting)
    db.session.commit()
    
    return redirect(url_for('meeting_room', id=meeting.id))

@app.route('/meeting/<int:id>')
@auth_required
def meeting_room(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return redirect(url_for('dashboard', error='Meeting not found'))
        
    banned = BannedUser.query.filter_by(meeting_id=meeting.id, user_id=g.user.id).first()
    if banned:
        return redirect(url_for('dashboard', error='You have been banned from this meeting.'))
        
    attendances = Attendance.query.filter_by(meeting_id=meeting.id).all()
    polls = Poll.query.filter_by(meeting_id=meeting.id).all()
    
    is_host = (meeting.host_id == g.user.id)
    user_attendance = next((a for a in attendances if a.user_id == g.user.id), None)
    
    # Generate QR
    qr_url = f"{request.url_root.rstrip('/')}/join/{meeting.id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_image = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return render_template('meeting_room.html',
        meeting=meeting,
        isHost=is_host,
        attendances=attendances,
        polls=polls,
        userAttendance=user_attendance,
        message=request.args.get('message'),
        error=request.args.get('error'),
        clientIp=get_client_ip(),
        url_origin=request.url_root.rstrip('/'),
        qrImage=qr_image,
        qrUrl=qr_url
    )

@app.route('/meeting/<int:id>/delete', methods=['POST'])
@auth_required
def delete_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return redirect(url_for('dashboard', error='Meeting not found'))
    if meeting.host_id != g.user.id:
        return redirect(url_for('dashboard', error='Unauthorized deletion'))
        
    AttendanceLog.query.filter(AttendanceLog.attendance_id.in_([a.id for a in Attendance.query.filter_by(meeting_id=meeting.id).all()])).delete(synchronize_session=False)
    Attendance.query.filter_by(meeting_id=meeting.id).delete()
    PollVote.query.filter(PollVote.poll_id.in_([p.id for p in Poll.query.filter_by(meeting_id=meeting.id).all()])).delete(synchronize_session=False)
    PollOption.query.filter(PollOption.poll_id.in_([p.id for p in Poll.query.filter_by(meeting_id=meeting.id).all()])).delete(synchronize_session=False)
    Poll.query.filter_by(meeting_id=meeting.id).delete()
    BannedUser.query.filter_by(meeting_id=meeting.id).delete()
    db.session.delete(meeting)
    db.session.commit()
    
    return redirect(url_for('dashboard', message='Meeting deleted successfully'))

@app.route('/meeting/<int:id>/kick/<int:user_id>', methods=['POST'])
@auth_required
def kick_user(id, user_id):
    meeting = Meeting.query.get(id)
    if not meeting or meeting.host_id != g.user.id:
        return redirect(url_for('dashboard', error='Unauthorized'))
    
    att = Attendance.query.filter_by(meeting_id=meeting.id, user_id=user_id).first()
    if att:
        AttendanceLog.query.filter_by(attendance_id=att.id).delete()
        db.session.delete(att)
        db.session.commit()
        return redirect(url_for('meeting_room', id=meeting.id, message='User kicked successfully'))
    return redirect(url_for('meeting_room', id=meeting.id, error='User not found'))

@app.route('/meeting/<int:id>/ban/<int:user_id>', methods=['POST'])
@auth_required
def ban_user(id, user_id):
    meeting = Meeting.query.get(id)
    if not meeting or meeting.host_id != g.user.id:
        return redirect(url_for('dashboard', error='Unauthorized'))
    
    if not BannedUser.query.filter_by(meeting_id=meeting.id, user_id=user_id).first():
        ban = BannedUser(meeting_id=meeting.id, user_id=user_id)
        db.session.add(ban)
    
    att = Attendance.query.filter_by(meeting_id=meeting.id, user_id=user_id).first()
    if att:
        AttendanceLog.query.filter_by(attendance_id=att.id).delete()
        db.session.delete(att)
    
    db.session.commit()
    return redirect(url_for('meeting_room', id=meeting.id, message='User banned successfully'))

@app.route('/attendance/<int:id>/delete', methods=['POST'])
@auth_required
def delete_attendance(id):
    att = Attendance.query.get(id)
    if not att:
        return redirect(url_for('dashboard', error='Attendance record not found'))
    if att.user_id != g.user.id:
        return redirect(url_for('dashboard', error='Unauthorized deletion'))
        
    AttendanceLog.query.filter_by(attendance_id=att.id).delete()
    db.session.delete(att)
    db.session.commit()
    return redirect(url_for('dashboard', message='Removed from your history'))

@app.route('/join/<int:id>')
@auth_required
def join_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return redirect(url_for('dashboard', error='Meeting not found'))
    if not meeting.active:
        return redirect(url_for('dashboard', error='This meeting has ended and attendance is closed.'))
        
    banned = BannedUser.query.filter_by(meeting_id=meeting.id, user_id=g.user.id).first()
    if banned:
        return redirect(url_for('dashboard', error='You have been banned from this meeting.'))
        
    existing = Attendance.query.filter_by(user_id=g.user.id, meeting_id=meeting.id).first()
    if existing:
        if existing.leave_date:
            existing.leave_date = None
            log = AttendanceLog(attendance_id=existing.id, type='join')
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('meeting_room', id=meeting.id, message='Successfully Re-joined'))
        return redirect(url_for('meeting_room', id=meeting.id, message='Successfully Joined'))
        
    client_ip_raw = get_client_ip() or ''
    clean_client_ip = client_ip_raw.split(',')[0].strip()
    clean_host_ip = (meeting.host_ip or '').split(',')[0].strip()
    
    if clean_client_ip != clean_host_ip:
        return redirect(url_for('dashboard', error=f'Attendance Denied! You are not on the same WiFi network as the Host. (Host Public IP: {clean_host_ip}, Your Public IP: {clean_client_ip})'))
        
    attendance = Attendance(user_id=g.user.id, meeting_id=meeting.id, method='wifi', ip_address=client_ip_raw)
    db.session.add(attendance)
    db.session.commit()
    
    log = AttendanceLog(attendance_id=attendance.id, type='join')
    db.session.add(log)
    db.session.commit()
    
    return redirect(url_for('meeting_room', id=meeting.id, message='Successfully Joined'))

@app.route('/meeting/<int:id>/leave', methods=['POST'])
@auth_required
def leave_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return redirect(url_for('dashboard', error='Meeting not found'))
        
    attendance = Attendance.query.filter_by(user_id=g.user.id, meeting_id=meeting.id).first()
    if not attendance:
        return redirect(url_for('meeting_room', id=meeting.id, error='Attendance record not found'))
        
    if not attendance.leave_date:
        attendance.leave_date = get_ist()
        log = AttendanceLog(attendance_id=attendance.id, type='leave')
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('meeting_room', id=meeting.id, message='Successfully Left'))
    else:
        return redirect(url_for('meeting_room', id=meeting.id, error='Already left'))

@app.route('/meeting/<int:id>/poll', methods=['POST'])
@auth_required
def create_poll(id):
    meeting = Meeting.query.get(id)
    if meeting.host_id != g.user.id:
        return "Unauthorized", 403
        
    question = request.form.get('question')
    options_text = request.form.get('options', '')
    
    poll = Poll(meeting_id=meeting.id, question=question)
    db.session.add(poll)
    db.session.commit()
    
    for opt in options_text.split('\n'):
        opt = opt.strip()
        if opt:
            poll_option = PollOption(poll_id=poll.id, text=opt)
            db.session.add(poll_option)
            
    db.session.commit()
    return redirect(url_for('meeting_room', id=meeting.id, message='Poll created'))

@app.route('/vote', methods=['POST'])
@auth_required
def vote():
    poll_id = request.form.get('pollId')
    option_id = request.form.get('optionId')
    meeting_id = request.form.get('meetingId')
    
    poll = Poll.query.get(poll_id)
    if not poll:
        return redirect(url_for('meeting_room', id=meeting_id, error='Poll not found'))
        
    has_voted = PollVote.query.filter_by(poll_id=poll.id, user_id=g.user.id).first()
    if has_voted:
        return redirect(url_for('meeting_room', id=meeting_id, error='Already voted'))
        
    option = PollOption.query.get(option_id)
    if not option or option.poll_id != poll.id:
        return redirect(url_for('meeting_room', id=meeting_id, error='Option not valid'))
        
    option.votes += 1
    vote_record = PollVote(poll_id=poll.id, user_id=g.user.id, option_id=option.id)
    db.session.add(vote_record)
    db.session.commit()
    
    return redirect(url_for('meeting_room', id=meeting_id, message='Vote Cast successfully'))

@app.route('/meeting/<int:id>/end', methods=['POST'])
@auth_required
def end_meeting(id):
    meeting = Meeting.query.get(id)
    if meeting.host_id != g.user.id:
        return "Unauthorized", 403
        
    meeting.active = False
    db.session.commit()
    return redirect(url_for('meeting_room', id=meeting.id, message='Meeting ended successfully'))

@app.route('/meeting/<int:id>/api/data')
@auth_required
def get_meeting_data(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify({'error': 'Not found'}), 404
        
    is_host = meeting.host_id == g.user.id
    user_attendance = Attendance.query.filter_by(meeting_id=meeting.id, user_id=g.user.id).first()
    
    if not is_host and (not user_attendance or user_attendance.leave_date):
        return jsonify({
            'active': meeting.active,
            'attendances': [],
            'polls': [],
            'userId': str(g.user.id)
        })
        
    attendances = Attendance.query.filter_by(meeting_id=meeting.id).order_by(Attendance.date.desc()).all()
    polls = Poll.query.filter_by(meeting_id=meeting.id).all()
    
    attendances_data = []
    for a in attendances:
        log_data = [{'type': l.type, 'timestamp': l.timestamp.isoformat()} for l in getattr(a, 'log', [])]
        attendances_data.append({
            'userId': {'_id': str(a.user_id), 'username': a.user.username},
            'log': log_data,
            'date': a.date.isoformat(),
            'leaveDate': a.leave_date.isoformat() if a.leave_date else None
        })
        
    polls_data = []
    for p in polls:
        voted_users = [{'userId': {'_id': str(v.user_id)}, 'optionId': v.option_id} for v in p.voted_users]
        options_data = [{'_id': str(o.id), 'text': o.text, 'votes': o.votes} for o in p.options]
        polls_data.append({
            '_id': str(p.id),
            'question': p.question,
            'votedUsers': voted_users,
            'options': options_data
        })
        
    return jsonify({
        'active': meeting.active,
        'attendances': attendances_data,
        'polls': polls_data,
        'userId': str(g.user.id)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)), debug=True)
