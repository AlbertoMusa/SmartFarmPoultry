from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
import json
from werkzeug.security import check_password_hash
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/SmartFarmPoultry'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class UserFarm(db.Model):
    _tablename_ = 'UserFarm'
    pub_id = db.Column('pub_id', db.String(100), primary_key=True)
    pri_id = db.Column('pri_id', db.String(100), unique=True) #crypt
    time_sam = db.Column('time_sam', db.DateTime)
    time_con = db.Column('time_con', db.DateTime)
    lux = db.Column('time', db.Integer)
    timeled_open = db.Column('timeled_open', db.DateTime)
    timeled_close = db.Column('timeled_close', db.DateTime)
    timedoor_open = db.Column('timedoor_open', db.DateTime)
    timedoor_close = db.Column('timedoor_close', db.DateTime)
    timenest_open = db.Column('timenest_open', db.DateTime)
    timenest_close = db.Column('timenest_close', db.DateTime)
    timeksr_open = db.Column('timeksr_open', db.DateTime)
    timeksr_close = db.Column('timeksr_close', db.DateTime)
    timeonfly_open = db.Column('timeonfly_open', db.DateTime)
    timeonfly_close = db.Column('timeonfly_close', db.DateTime)
    a_lux = db.Column('a_lux', db.Integer)
    a_hysteresis = db.Column('a_hysteresis', db.Integer)
    b_lux = db.Column('b_lux', db.Integer)
    b_hysteresis = db.Column('b_hysteresis', db.Integer)

    @property
    def serialize(self):
        return {
            'pub_id': self.pub_id,
            'lux': self.lux
            # continue...
        }

class UserDevice(UserMixin, db.Model):
    _tablename_ = 'UserDevice'
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(100), unique=True)
    password = db.Column('password', db.String(100)) #crypt

class Motor(db.Model):
    _tablename_ = 'Motor'
    motor_id = db.Column('motor_id', db.Integer, primary_key=True) #1-7
    farm_id = db.Column('farm_id', db.String(100), db.ForeignKey('UserFarm.pub_id'))
    addresses = db.Column('addresses', db.String(20))
    numbers = db.Column('numbers', db.String(10))
    time_ready = db.Column('time_ready', db.Integer)
    active = db.Column('active', db.Boolean)

    @property
    def serialize(self):
        return {
            'motor_id': self.motor_id,
            'farm_id': self.farm_id,
            'addresses': self.addresses
        }

class Led(db.Model):
    _tablename_ = 'Led'
    led_id = db.Column('led_id', db.Integer, primary_key=True) #1-6
    farm_id = db.Column('farm_id', db.String(100), db.ForeignKey('UserFarm.pub_id'))
    addresses = db.Column('addresses', db.String(20))
    numbers = db.Column('numbers', db.String(10))
    max_value = db.Column('max_value', db.Integer)
    dim_up_delay = db.Column('dim_up_delay', db.Integer)
    dim_down_delay = db.Column('dim_down_delay', db.Integer)
    dim_time = db.Column('dim_time', db.Integer)
    active = db.Column('active', db.Boolean)

    @property
    def serialize(self):
        return {
            'led_id': self.led_id,
            'farm_id': self.farm_id,
            'addresses': self.addresses
        }

class Change(db.Model):
    _tablename_ = 'Change'
    change_id = db.Column('change_id', db.String(100), primary_key=True, autoincrement=True)
    farm_id = db.Column('farm_id', db.String(100), db.ForeignKey('UserFarm.pub_id'))
    code = db.Column('code', db.String(10))
    val = db.Column('val', db.String(10))
    time_req = db.Column('time_req', db.DateTime)
    flag = db.Column('flag', db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return UserDevice.query.get(user_id)

@app.route('/login')
def login():
    auth = request.authorization
    prec = UserDevice.query.filter_by(username=auth.username)
    if prec is None:
        return 1
    if check_password_hash(prec.password, auth.password):
        db.session.commit()
        login_user(prec)
        return 0
    return 2

@app.route('/logout')
@login_required
def logout():
    logout_user()

@app.route('/getFarms')
@login_required
def get_farms():
    farms = UserFarm.query.with_entities(UserFarm.pub_id).all()
    data = []
    for element in farms:
        data.append({id: element.pub_id})
    jsondata=json.dumps(data)
    return jsondata

@app.route('/getLeds')
@login_required
def get_leds():
    req = request.get_json()
    leds = Led.query.filter_by(farm_id=req['id']).with_entities(Led.led_id).all()
    data = []
    for element in leds:
        data.append({id: element.led_id})
    jsondata = json.dumps(data)
    return jsondata

@app.route('/getMotors')
@login_required
def get_motors():
    req = request.get_json()
    motors = Motor.query.filter_by(farm_id=req['id']).with_entities(Motor.motor_id).all()
    data = []
    for element in motors:
        data.append({id: element.led_id})
    jsondata = json.dumps(data)
    return jsondata

@app.route('/getFarm')
@login_required
def get_farm():
    req = request.get_json()
    farm = UserFarm.query.filter_by(pub_id=req['id'])
    return farm.serialize

@app.route('/getLed')
@login_required
def get_led():
    req = request.get_json()
    led = Led.query.filter_by(farm_id=req['farm_id'], led_id=req['led_id'])
    return led.serialize

@app.route('/getMotor')
@login_required
def get_motor():
    req = request.get_json()
    motor = Motor.query.filter_by(farm_id=req['farm_id'], motor_id=req['motor_id'])
    return motor.serialize

@app.route('/setChange')
@login_required
def set_led():
    req = request.get_json()
    ch = Change(farm_id=req['farm_id'], code=req['code'], value=req['value'], time=datetime.datetime.utcnow)
    db.session.add(ch)
    db.session.commit()
    return 0

if __name__ == '__main__':
    app.run(debug=True)