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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost/SmartFarmPoultry2'

from Db.models2 import db
db.init_app(app)

from Db.models2 import UserFarm
from Db.models2 import Farm
from Db.models2 import Session
from Db.models2 import Motor
from Db.models2 import Led
from Db.models2 import Change

#------------------------------------------ CHANGES MANAGER ------------------------------------------
def check_changes(db):
    #CAN BE DO WITH NORMAL DB CALL
    print("----------------------------------start thread----------------------------------") if deb2 else None
    while True:
        if Change.query.filter_by(flag=False).order_by(Change.time_req.desc()).first() is not None:
            app1 = Change.query.filter_by(flag=False).order_by(Change.time_req.desc()).first()
            if UserFarm.query.filter_by(pub_id=app1.pub_id).first() is not None:
                app2 = UserFarm.query.filter_by(pub_id=app1.pub_id).first()
                if Session.query.filter_by(pub_id=app1.pub_id, flag=True).first() is not None:
                    app3 = Session.query.filter_by(pub_id=app1.pub_id, flag=True).first()
                    data = {"ses_id": app3.session_id, 'dev': app1.dev, 'code': app1.code, 'val': app1.val, 'time_req': app1.time_req.strftime("%m/%d/%Y, %H:%M:%S.%f")}
                    print("TH-data: ", data) if deb else None
                    crypt_data = jws.sign(data, jws.verify(app2.pri_id, priv_id, algorithms=['HS256']).decode(), algorithm='HS256')
                    print("TH-encrypt data: ", crypt_data) if deb else None
                    sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
                    print("TH-sign of data: ", sign_crypt_data) if deb else None
                    req = {"pub_id": app2.pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
                    print("TH-send: ", req) if deb else None
                    emit('changes', req, room=app3.sid)
                    print("TH CHECK CHANGE ---> user: ", app2.pub_id) if deb2 else None
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
                canc = Change.query.filter_by(flag=False, time_req=datetime.datetime.strptime(req_data['time_req'], "%m/%d/%Y, %H:%M:%S.%f"), pub_id=req['pub_id']).order_by(Change.time_req.asc()).first()
                canc.flag = True
                db.session.commit()
                print("TH CHANGE CONF ---> user: ", app1.pub_id) if deb2 else None
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
                if Farm.query.filter_by(pub_id=req['pub_id']).first() is not None:
                    app3 = Farm.query.filter_by(pub_id=req['pub_id']).order_by(Farm.time_sam.desc(), Farm.time_con.desc()).first()
                    row = app3.duplicate
                else:
                    row = Farm(pub_id=req['pub_id'], time_con=datetime.datetime(1, 1, 1, 0, 0), time_sam=datetime.datetime(1, 1, 1, 0, 0))
                if row.time_sam > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S') and row.time_con > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                        emit('sample_response', 6)
                else:
                    if row.time_sam < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                        row.lux = req_data['data']['lightsensor']
                        print("lightsensor: ", req_data['data']['lightsensor']) if deb else None
                        row.time_sam = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                        if row.time_con < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                            db.session.add(row)
                            for x in range(1, 8):
                                if Motor.query.filter_by(farm_id=req['pub_id'], motor_id=x).first() is not None:
                                    app4 = Motor.query.filter_by(farm_id=req['pub_id'], motor_id=x).order_by(Motor.time_sam.desc(), Motor.time_con.desc()).first()
                                    mot = app4.duplicate
                                else:
                                    mot = Motor(farm_id=req['pub_id'], motor_id=x, time_sam=datetime.datetime(1, 1, 1, 0, 0), time_con=datetime.datetime(1, 1, 1, 0, 0))
                                mot.active = req_data['data'][mot_sam[x-1]]
                                mot.time_sam = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                                db.session.add(mot)
                                print("Motor ", x, ": ", req_data['data'][mot_sam[x-1]]) if deb else None
                            for x in range(1, 7):
                                if Led.query.filter_by(farm_id=req['pub_id'], led_id=x).first() is not None:
                                    app4 = Led.query.filter_by(farm_id=req['pub_id'], led_id=x).order_by(Led.time_sam.desc(), Led.time_con.desc()).first()
                                    led = app4.duplicate
                                else:
                                    led = Led(farm_id=req['pub_id'], led_id=x, time_con=datetime.datetime(1, 1, 1, 0, 0), time_sam=datetime.datetime(1, 1, 1, 0, 0))
                                led.max_value = req_data['data'][le_sam[x-1]]
                                led.time_sam = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                                db.session.add(led)
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
                if Farm.query.filter_by(pub_id=req['pub_id']).first() is not None:
                    app3 = Farm.query.filter_by(pub_id=req['pub_id']).order_by(Farm.time_sam.desc(), Farm.time_con.desc()).first()
                    row = app3.duplicate
                else:
                    row = Farm(pub_id=req['pub_id'], time_con=datetime.datetime(1, 1, 1, 0, 0), time_sam=datetime.datetime(1, 1, 1, 0, 0))
                if row.time_sam > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S') and row.time_con > datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                    emit('sample_response', 6)
                else:
                    if row.time_con < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                        row.time_con = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                        row.timeled_open_h = req_data['config']['timeLED']['openHour']
                        row.timeled_open_m = req_data['config']['timeLED']['openMinute']
                        row.timeled_close_h = req_data['config']['timeLED']['closeHour']
                        row.timeled_close_m = req_data['config']['timeLED']['closeMinute']
                        row.timedoor_open_h =req_data['config']['timeDoor']['openHour']
                        row.timedoor_open_m = req_data['config']['timeDoor']['openMinute']
                        row.timedoor_close_h = req_data['config']['timeDoor']['closeHour']
                        row.timedoor_close_m =req_data['config']['timeDoor']['closeMinute']
                        row.timenest_open_h = req_data['config']['timeNest']['openHour']
                        row.timenest_open_m = req_data['config']['timeNest']['openMinute']
                        row.timenest_close_h = req_data['config']['timeNest']['closeHour']
                        row.timenest_close_m = req_data['config']['timeNest']['closeMinute']
                        row.timeksr_open_h = req_data['config']['timeKsr']['openHour']
                        row.timeksr_open_m = req_data['config']['timeKsr']['openMinute']
                        row.timeksr_close_h = req_data['config']['timeKsr']['closeHour']
                        row.timeksr_close_m = req_data['config']['timeKsr']['closeMinute']
                        row.timeonfly_open_h = req_data['config']['timeOnFly']['openHour']
                        row.timeonfly_open_m = req_data['config']['timeOnFly']['openMinute']
                        row.timeonfly_close_h = req_data['config']['timeOnFly']['closeHour']
                        row.timeonfly_close_m = req_data['config']['timeOnFly']['closeMinute']
                        row.a_lux = req_data['config']['closeDoorBrightness']['lux']
                        row.a_hysteresis = req_data['config']['closeDoorBrightness']['hysteresis']
                        row.b_lux = req_data['config']['ledOffBrightness']['lux']
                        row.b_hysteresis = req_data['config']['ledOffBrightness']['hysteresis']
                        db.session.add(row)
                        for x in range(1, 8):
                            if Motor.query.filter_by(farm_id=req['pub_id'], motor_id=x).first() is not None:
                                app4 = Motor.query.filter_by(farm_id=req['pub_id'], motor_id=x).order_by(
                                    Motor.time_sam.desc(), Motor.time_con.desc()).first()
                                mot = app4.duplicate
                            else:
                                mot = Motor(farm_id=req['pub_id'], motor_id=x, time_sam=datetime.datetime(1, 1, 1, 0, 0), time_con=datetime.datetime(1, 1, 1, 0, 0))
                            print("Motor ", x, ": ", req_data['config'][mot_con[x-1]]['addresses']) if deb else None
                            mot.addresses = req_data['config'][mot_con[x-1]]['addresses']
                            mot.numbers = req_data['config'][mot_con[x-1]]['numbers']
                            mot.time_ready = req_data['config'][mot_con[x-1]]['time']
                            mot.time_con = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                            if mot.time_sam < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                                mot.active = req_data['config'][mot_con[x-1]]['active']
                            db.session.add(mot)
                        for x in range(1, 7):
                            if Led.query.filter_by(farm_id=req['pub_id'], led_id=x).first() is not None:
                                app4 = Led.query.filter_by(farm_id=req['pub_id'], led_id=x).order_by(
                                    Led.time_sam.desc(), Led.time_con.desc()).first()
                                led = app4.duplicate
                            else:
                                led = Led(farm_id=req['pub_id'], led_id=x, time_con=datetime.datetime(1, 1, 1, 0, 0), time_sam=datetime.datetime(1, 1, 1, 0, 0))
                            print("Led ", x, ": ", req_data['config'][le_con[x-1]]['addresses']) if deb else None
                            led.addresses = req_data['config'][le_con[x-1]]['addresses']
                            led.numbers = req_data['config'][le_con[x-1]]['numbers']
                            led.dim_up_delay = req_data['config'][le_con[x-1]]['dimUpDelay']
                            led.dim_down_delay = req_data['config'][le_con[x-1]]['dimDownDelay']
                            led.dim_time = req_data['config'][le_con[x-1]]['dimTime']
                            led.active = req_data['config'][le_con[x-1]]['active']
                            led.time_con = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                            if led.time_sam < datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S'):
                                led.max_value = req_data['config'][le_con[x-1]]['maxValue']
                            db.session.add(led)
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