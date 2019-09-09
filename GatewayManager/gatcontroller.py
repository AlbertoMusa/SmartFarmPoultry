#------------------------------------------ LIBRARY ------------------------------------------
#import eventlet
from flask import Flask, request
from flask_socketio import SocketIO, emit
from Crypto.PublicKey import RSA
import datetime
import json
import time
import secrets
from jose import jws
import threading
from Utility import sign

import eventlet
eventlet.monkey_patch()

import string
alphabet = string.ascii_letters + string.digits

#------------------------------------------ GLOBAL VAR ------------------------------------------
key = RSA.generate(1024)
mot_sam = ["leftFrontFlap", "leftBackFlap", "rightFrontFlap", "rightBackFlap", "nestFlap", "ksrFlap", "onFlyPole"]
le_sam = ["topLED", "midLED", "bottomLED", "nestLED", "ksrLED", "alwaysLED"]
mot_con = ["flapLeftFront", "flapLeftBack", "flapRightFront", "flapRightBack", "nestEject", "flapKsr", "onFlyPole"]
le_con = ["LEDTop", "LEDMid", "LEDBottom", "LEDNest", "LEDKsr", "LEDAlways"]
priv_id = "password"
deb = False #DEBUG
deb2 = True #DEBUG
thread = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

#------------------------------------------ SERVER SETUP ------------------------------------------
# import sys
# import eventlet.wsgi
# eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), app)

#------------------------------------------ DB INIT------------------------------------------
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost/SmartFarmPoultry'

from Db.models import db
db.init_app(app)

from Db.models import UserFarm
from Db.models import Session
from Db.models import Motor
from Db.models import Led
from Db.models import Change

#------------------------------------------ CHANGES MANAGER ------------------------------------------
def check_changes(db):
    #CAN BE DO WITH NORMAL DB CALL
    print("----------------------------------start thread----------------------------------") if deb2 else None
    while True:
        if db.session.query(Change).filter_by(flag=False).order_by(Change.time_req.asc()).first() is not None:
            app1 = db.session.query(Change).filter_by(flag=False).order_by(Change.time_req.asc()).first()
            if db.session.query(UserFarm).filter_by(pub_id=app1.farm_id).first() is not None:
                app2 = db.session.query(UserFarm).filter_by(pub_id=app1.farm_id).first()
                if db.session.query(Session).filter_by(pub_id=app1.farm_id, flag=True).first() is not None:
                    app3 = db.session.query(Session).filter_by(pub_id=app1.farm_id, flag=True).first()
                    data = {"ses_id": app3.session_id, 'code': app1.code, 'val': app1.val, "ch_id": app1.change_id}
                    print("TH-data: ", data) if deb else None
                    crypt_data = jws.sign(data, jws.verify(app2.pri_id, priv_id, algorithms=['HS256']).decode(), algorithm='HS256')
                    print("TH-encrypt data: ", crypt_data) if deb else None
                    sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
                    print("TH-sign of data: ", sign_crypt_data) if deb else None
                    req = {"pub_id": app2.pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
                    print("TH-send: ", req) if deb else None
                    emit('changes', req, room=app3.sid)
                    print("TH CHECK CHANGE ---> user: ", app2.pub_id, "  ch_id: ", app1.change_id) if deb2 else None
        print("----------------------------------th restart loop----------------------------------") if deb2 else None
        time.sleep(5)
    print("----------------------------------finish thread----------------------------------") if deb2 else None

@socketio.on('change_confirm')
def change_confirm(req):
    print("----------------------------------change confirm----------------------------------") if deb2 else None
    print("received data: ", req) if deb else None
    print("received data pub_id: ", req['pub_id']) if deb else None
    print("received data data: ", req['data']) if deb else None
    print("received data sign: ", req['sign']) if deb else None
    if UserFarm.query.filter_by(pub_id=req['pub_id']).first() is not None:
        app1 = UserFarm.query.filter_by(pub_id=req['pub_id']).first()
        print("UserFarm pub: ", app1.pub_id) if deb else None
        print("UserFarm priv: ", app1.pri_id) if deb else None
        print("decrypt pass on db: ", jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode()) if deb else None
        try:
            req_data = json.loads(jws.verify(req['data'], jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode(), algorithms=['HS256']))
        except:
            pass
        print("decrypt data: ", req_data) if deb else None
        if Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first() is not None:
            app2 = Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first()
            if sign.verify_sign(app2.key, req['sign'], req['data']):
                print("valid sign") if deb else None
                canc = Change.query.filter_by(flag=False, change_id=req_data['ch_id'], farm_id=req['pub_id']).order_by(Change.time_req.asc()).first()
                canc.flag = True
                db.session.commit()
                print("TH CHANGE CONF ---> user: ", app1.pub_id, "  ch_id: ", req_data['ch_id']) if deb2 else None
                print("----------------------------------change confirm DONE----------------------------------") if deb2 else None

#------------------------------------------ ROUTES ------------------------------------------
@socketio.on('connect_request')
def connect_request(req):
    print("----------------------------------connect_request----------------------------------") if deb2 else None
    print("req pub_id: : ", req['pub_id']) if deb else None
    print("req key: ", req['key']) if deb else None
    print("req key encode utf-8: ", req['key'].encode('utf-8')) if deb else None
    if UserFarm.query.filter_by(pub_id=req['pub_id']).first() is not None:
        app1 = UserFarm.query.filter_by(pub_id=req['pub_id']).first()
        print("UserFarm pub_id: ", app1.pub_id) if deb else None
        if Session.query.filter_by(pub_id=req['pub_id'], flag=True).first() is not None:
            app2 = Session.query.filter_by(pub_id=req['pub_id'], flag=True).first()
            print("Session pub_id: ", app2.pub_id) if deb else None
            app2.flag = False
            app2.time_end = datetime.datetime.utcnow()
            db.session.commit()
        otp = ''.join(secrets.choice(alphabet) for i in range(50))
        print("otp: ", otp) if deb else None
        cur = Session(pub_id=req['pub_id'], key=req['key'], otp=otp, flag=True, time_start=datetime.datetime.utcnow())
        db.session.add(cur)
        db.session.commit()
        data = {"otp": otp, "key": key.publickey().export_key().decode("utf-8")}
        print("decrypt pass on db: ", jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode()) if deb else None
        crypt_data = jws.sign(data, jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode(), algorithm='HS256')
        print("encrypt data: ", crypt_data) if deb else None
        sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
        print("sign encrypt data: ", sign_crypt_data) if deb else None
        resp = {"data": crypt_data, "sign": sign_crypt_data.decode()}
        print("resp: ", resp) if deb else None
        print("resp data: ", resp['data']) if deb else None
        print("CON REQ ---> user: ", app1.pub_id) if deb2 else None
        print("----------------------------------connect_request DONE----------------------------------") if deb2 else None
        emit('connect_response', resp)
    else:
        emit('connect_response', 1)

@socketio.on('connect_confirm')
def connect_confirm(req):
    print("----------------------------------connect confirm----------------------------------") if deb2 else None
    print("received data: ", req) if deb else None
    print("received data pub_id: ", req['pub_id']) if deb else None
    print("received data data: ", req['data']) if deb else None
    print("received data sign: ", req['sign']) if deb else None
    if UserFarm.query.filter_by(pub_id=req['pub_id']).first() is not None:
        app1 = UserFarm.query.filter_by(pub_id=req['pub_id']).first()
        print("UserFarm pub: ", app1.pub_id) if deb else None
        print("UserFarm priv: ", app1.pri_id) if deb else None
        print("decrypt pass on db: ", jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode()) if deb else None
        try:
            req_data = json.loads(jws.verify(req['data'], jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode(), algorithms=['HS256']))
        except:
            emit('connect_estab', 5)
        print("decrypt data: ", req_data) if deb else None
        if Session.query.filter_by(otp=req_data['otp'], flag=True).first() is not None:
            app2 = Session.query.filter_by(otp=req_data['otp'], flag=True).first()
            if sign.verify_sign(app2.key, req['sign'], req['data']):
                print("valid sign") if deb else None
                print("time_start : ", app2.time_start) if deb else None
                print("now - delta : ", datetime.datetime.utcnow() - datetime.timedelta(minutes=10)) if deb else None
                if app2.time_start > datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                    ses_id = ''.join(secrets.choice(alphabet) for i in range(100))
                    app2.session_id = ses_id
                    print("sid: ", request.sid) if deb else None
                    app2.sid = request.sid
                    db.session.commit()
                    data = {"ses_id": ses_id}
                    print("data resp: ", data) if deb else None
                    print("app1.pri_id: ",  jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode()) if deb else None
                    crypt_data = jws.sign(data,  jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode(), algorithm='HS256')
                    print("encrypt data to send: ", crypt_data) if deb else None
                    sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
                    print("sign of en data send: ", sign_crypt_data) if deb else None
                    res2 = {"pub_id": app2.pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
                    print("send: ", res2) if deb else None
                    print("TH CON CONF ---> user: ", app1.pub_id, "  ses_id: ",  ses_id) if deb2 else None
                    print("----------------------------------connect_confirm DONE----------------------------------") if deb2 else None
                    emit('connect_estab', res2)

                    global thread
                    if thread is None:
                        #thread = socketio.start_background_task(check_changes, app, db)
                        thread = threading.Thread(target=check_changes(db))
                        thread.start()

                else:
                    emit('connect_estab', 4)
            else:
                emit('connect_estab', 3)
        else:
            emit('connect_estab', 2)
    else:
        emit('connect_estab', 1)

@socketio.on('discon')
def disconnect(req):
    print("----------------------------------disconnect----------------------------------") if deb2 else None
    print("received data: ", req) if deb else None
    print("received data pub_id: ", req['pub_id']) if deb else None
    print("received data data: ", req['data']) if deb else None
    print("received data sign: ", req['sign']) if deb else None
    if UserFarm.query.filter_by(pub_id=req['pub_id']).first() is not None:
        app1 = UserFarm.query.filter_by(pub_id=req['pub_id']).first()
        print("UserFarm pub: ", app1.pub_id) if deb else None
        print("UserFarm priv: ", app1.pri_id) if deb else None
        print("decrypt pass on db: ", jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode()) if deb else None
        try:
            req_data = json.loads(
                jws.verify(req['data'], jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode(), algorithms=['HS256']))
        except:
            emit('connect_estab', 5)
        print("decrypt data: ", req_data) if deb else None
        if Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first() is not None:
            app2 = Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first()
            if sign.verify_sign(app2.key, req['sign'], req['data']):
                print("valid sign") if deb else None
                app2.flag = False
                app2.time_end = datetime.datetime.utcnow()
                db.session.commit()
                print("DISC ---> user: ", app1.pub_id, "  ses_id: ", req_data['ses_id']) if deb2 else None
                print("----------------------------------disconnect DONE----------------------------------") if deb2 else None
                emit('disc_response', 0)
            else:
                emit('disc_response', 2)
        else:
            emit('disc_response', 3)
    else:
        emit('disc_response', 1)

@socketio.on('sample_dict')
def sample_dict(req):
    print("----------------------------------sample dict----------------------------------") if deb2 else None
    print("received data: ", req) if deb else None
    print("received data pub_id: ", req['pub_id']) if deb else None
    print("received data data: ", req['data']) if deb else None
    print("received data sign: ", req['sign']) if deb else None
    if UserFarm.query.filter_by(pub_id=req['pub_id']).first() is not None:
        app1 = UserFarm.query.filter_by(pub_id=req['pub_id']).first()
        print("UserFarm pub: ", app1.pub_id) if deb else None
        print("UserFarm priv: ", app1.pri_id) if deb else None
        print("decrypt pass on db: ", jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode()) if deb else None
        try:
            req_data = json.loads(jws.verify(req['data'], jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode(), algorithms=['HS256']))
        except:
            emit('samp_response', 5)
        print("decrypt data: ", req_data) if deb else None
        if Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first() is not None:
            app2 = Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first()
            if sign.verify_sign(app2.key, req['sign'], req['data']):
                print("valid sign") if deb else None
                if app1.time_sam > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S') and app1.time_con > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                    emit('sample_response', 6)
                else:
                    if app1.time_sam < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                        app1.lux = req_data['data']['lightsensor']
                        print("lightsensor: ", req_data['data']['lightsensor']) if deb else None
                        app1.time_sam = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                        if app1.time_con < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                            for x in range(1, 8):
                                app3 = Motor.query.filter_by(farm_id=req['pub_id'], motor_id=x).first()
                                app3.active = req_data['data'][mot_sam[x-1]]
                                print("Motor ", x, ": ", req_data['data'][mot_sam[x-1]]) if deb else None
                            for x in range(1, 7):
                                app3 = Led.query.filter_by(farm_id=req['pub_id'], led_id=x).first()
                                app3.max_value = req_data['data'][le_sam[x-1]]
                                print("Led ", x, ": ", req_data['data'][mot_sam[x-1]]) if deb else None
                        db.session.commit()
                        print("SAMP DICT ---> user: ", app1.pub_id, "  ses_id: ", req_data['ses_id']) if deb2 else None
                        print("----------------------------------ample_dict DONE----------------------------------") if deb2 else None
                        emit('samp_response', 0)
                    else:
                        emit('samp_response', 6)
            else:
                emit('samp_response', 3)

@socketio.on('configuration_dict')
def configuration_dict(req):
    print("----------------------------------configuration dict----------------------------------") if deb2 else None
    print("received data: ", req) if deb else None
    print("received data pub_id: ", req['pub_id']) if deb else None
    print("received data data: ", req['data']) if deb else None
    print("received data sign: ", req['sign']) if deb else None
    if UserFarm.query.filter_by(pub_id=req['pub_id']).first() is not None:
        app1 = UserFarm.query.filter_by(pub_id=req['pub_id']).first()
        print("UserFarm pub: ", app1.pub_id) if deb else None
        print("UserFarm priv: ", app1.pri_id) if deb else None
        print("decrypt pass on db: ", jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode()) if deb else None
        try:
            req_data = json.loads(jws.verify(req['data'], jws.verify(app1.pri_id, priv_id, algorithms=['HS256']).decode(),algorithms=['HS256']))
        except:
            emit('conf_response', 5)
        print("decrypt data: ", req_data) if deb else None
        if Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first() is not None:
            app2 = Session.query.filter_by(session_id=req_data['ses_id'], pub_id=req['pub_id'], flag=True).first()
            if sign.verify_sign(app2.key, req['sign'], req['data']):
                print("valid sign") if deb else None
                if app1.time_sam > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S') and app1.time_con > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                    emit('sample_response', 6)
                else:
                    if app1.time_con < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                        app1.time_con = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                        app1.timeled_open_h = req_data['config']['timeLED']['openHour']
                        app1.timeled_open_m = req_data['config']['timeLED']['openMinute']
                        app1.timeled_close_h = req_data['config']['timeLED']['closeHour']
                        app1.timeled_close_m = req_data['config']['timeLED']['closeMinute']
                        app1.timedoor_open_h =req_data['config']['timeDoor']['openHour']
                        app1.timedoor_open_m = req_data['config']['timeDoor']['openMinute']
                        app1.timedoor_close_h = req_data['config']['timeDoor']['closeHour']
                        app1.timedoor_close_m =req_data['config']['timeDoor']['closeMinute']
                        app1.timenest_open_h = req_data['config']['timeNest']['openHour']
                        app1.timenest_open_m = req_data['config']['timeNest']['openMinute']
                        app1.timenest_close_h = req_data['config']['timeNest']['closeHour']
                        app1.timenest_close_m = req_data['config']['timeNest']['closeMinute']
                        app1.timeksr_open_h = req_data['config']['timeKsr']['openHour']
                        app1.timeksr_open_m = req_data['config']['timeKsr']['openMinute']
                        app1.timeksr_close_h = req_data['config']['timeKsr']['closeHour']
                        app1.timeksr_close_m = req_data['config']['timeKsr']['closeMinute']
                        app1.timeonfly_open_h = req_data['config']['timeOnFly']['openHour']
                        app1.timeonfly_open_m = req_data['config']['timeOnFly']['openMinute']
                        app1.timeonfly_close_h = req_data['config']['timeOnFly']['closeHour']
                        app1.timeonfly_close_m = req_data['config']['timeOnFly']['closeMinute']
                        app1.a_lux = req_data['config']['closeDoorBrightness']['lux']
                        app1.a_hysteresis = req_data['config']['closeDoorBrightness']['hysteresis']
                        app1.b_lux = req_data['config']['ledOffBrightness']['lux']
                        app1.b_hysteresis = req_data['config']['ledOffBrightness']['hysteresis']
                        for x in range(1, 8):
                            print("Motor ", x, ": ", req_data['config'][mot_con[x-1]]['addresses']) if deb else None
                            app3 = Motor.query.filter_by(farm_id=req['pub_id'], motor_id=x).first()
                            app3.addresses = req_data['config'][mot_con[x-1]]['addresses']
                            app3.numbers = req_data['config'][mot_con[x-1]]['numbers']
                            app3.time_ready = req_data['config'][mot_con[x-1]]['time']
                            if app1.time_sam < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                                app3.active = req_data['config'][mot_con[x-1]]['active']
                        for x in range(1, 7):
                            print("Led ", x, ": ", req_data['config'][le_con[x-1]]['addresses']) if deb else None
                            app3 = Led.query.filter_by(farm_id=req['pub_id'], led_id=x).first()
                            app3.addresses = req_data['config'][le_con[x-1]]['addresses']
                            app3.numbers = req_data['config'][le_con[x-1]]['numbers']
                            app3.dim_up_delay = req_data['config'][le_con[x-1]]['dimUpDelay']
                            app3.dim_down_delay = req_data['config'][le_con[x-1]]['dimDownDelay']
                            app3.dim_time = req_data['config'][le_con[x-1]]['dimTime']
                            app3.active = req_data['config'][le_con[x-1]]['active']
                            if app1.time_sam < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                                app3.max_value = req_data['config'][le_con[x-1]]['maxValue']
                        db.session.commit()
                        print("CONF DICT ---> user: ", app1.pub_id, "  ses_id: ", req_data['ses_id']) if deb2 else None
                        print("----------------------------------configuration_sample DONE----------------------------------") if deb2 else None
                        emit('conf_response', 0)
                    else:
                        emit('conf_response', 6)
            else:
                emit('conf_response', 2)
        else:
            emit('conf_response', 3)
    else:
        emit('conf_response', 1)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
