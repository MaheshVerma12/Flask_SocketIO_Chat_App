import os 
import random 
import logging
from datetime import datetime 
from typing import Dict 


from flask import Flask, render_template, request, session 
from flask_socketio import SocketIO, send, emit, join_room, leave_room 
from werkzeug.middleware.proxy_fix import ProxyFix 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger=logging.getLogger(__name__)

class Config:
    SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(24)
    DEBUG=os.environ.get("FLASK_DEBUG", "False").lower() in {"1", "true", "yes", "on"}
    CORS_ORIGINS=os.environ.get("CORS_ORIGINS", "*")

    CHAT_ROOMS=[
        "General",
        "Zero to Knowing",
        "Code with Mahesh",
        "The Nerd Nook"
    ]

app=Flask(__name__)
app.config.from_object(Config)

# Handle reverse proxy 
app.wsgi_app=ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Set up socket 
socketIO=SocketIO(app=app, cors_allowed_origins=app.config["CORS_ORIGINS"], logger=True, engineio_logger=True) 

# Make a dictionary to store the active users.
active_users: Dict[str, dict]={}

# Make a user 
def generate_guest_username() -> str:
    timestamp=datetime.now().strftime("%H%M")
    return f"Guest{timestamp}{random.randint(100,999)}"

# Home Route 
@app.route("/")
def index():
    if 'username' not in session:
        session['username']=generate_guest_username()
        logger.info(f"New user session made: {session['username']}")

    return render_template('index.html', username=session['username'], rooms=app.config["CHAT_ROOMS"])


# Make a connection 
@socketIO.event
def connect():
    try:
        if 'username' not in session:
            session['username']=generate_guest_username()
        active_users[request.sid]={
            'username':session['username'],
            'connected_at':datetime.now().isoformat()
        }
        emit('active_users', {
            'users':[user['username'] for user in active_users.values()]
        }, broadcast=True) 

        logger.info(f"User connected: {session['username']}")

    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False 

@socketIO.event 
def disconnect():
    try:
        if request.sid in active_users:
            username=active_users[request.sid]['username']
            del active_users[request.sid]
            
            emit("active_users", {
                    'users':[user['username'] for user in active_users.values()]
            
                }, broadcast=True)
            
            logger.info(f"User {username} has left the chat!")

    except Exception as e:
        logger.error(f"Disconnection error: {str(e)}")

@socketIO.on("join")
def on_join(data:dict):
    try:
        username=session['username']
        room=(data.get('room') or 'General').strip()

        if room not in app.config['CHAT_ROOMS']:
            logger.warning(f"Room {room} is not in the valid rooms!")
            return

        join_room(room=room)
        if request.sid in active_users:
            active_users[request.sid]['room'] = room
        emit('status', {
            'msg':f"{username} has joined the room.",
            'type':'join',
            'timestamp':datetime.now().isoformat()
        }, room=room)
        logger.info(f"User {username} has joined {room}!")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")

@socketIO.on("leave")
def on_leave(data:dict):
    try:
        username=session["username"]
        room=(data.get('room') or 'General').strip()

        if room in app.config['CHAT_ROOMS']:
            leave_room(room)
        if request.sid in active_users:
            active_users[request.sid].pop('room', None)

        emit('status', {
            'msg':f"{username} has left the room!",
            "type":"leave",
            'timestamp':datetime.now().isoformat()
        }, room=room)
        logger.info(f"{username} has left the room.")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")


@socketIO.on("message")
def handle_messages(data:dict):
    try:
        username=session['username']
        room=data.get('room',"General")
        msg_type=data.get("type", "message")
        message=data.get('msg',"").strip()

        if not message:
            return 

        timestamp=datetime.now().isoformat()

        if msg_type=="private":
            target_user=data.get('target')
            if not target_user:
                return 
            for sid, user_data in active_users.items():
                if user_data['username']==target_user:
                    emit('private_message',{
                        'msg':message,
                        'from':username,
                        'to':target_user,
                        'timestamp':timestamp
                    }, room=sid)
                    return 

        else:
            if room not in app.config["CHAT_ROOMS"]:
                return 
            emit('message',{
                'msg':message,
                'username':username,
                'room':room,
                'timestamp':timestamp
            }, room=room) 

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
            

if __name__=="__main__":
    port=int(os.environ.get('PORT',5000))
    socketIO.run(
        app,
        host='0.0.0.0',
        port=port, 
        debug=app.config["DEBUG"],
        use_reloader=app.config["DEBUG"]
    ) 