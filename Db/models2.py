from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class UserFarm(db.Model):
    __tablename__ = 'userfarm'
    pub_id = db.Column('pub_id', db.String(100), primary_key=True)
    pri_id = db.Column('pri_id', db.String(200), unique=True)

class Farm(db.Model):
    __tablename__ = 'farm'
    pub_id = db.Column('pub_id', db.String(100), db.ForeignKey('userfarm.pub_id'), primary_key=True)
    time_sam = db.Column('time_sam', db.DateTime, primary_key=True)
    time_con = db.Column('time_con', db.DateTime, primary_key=True)
    lux = db.Column('lux', db.Integer)
    timeled_open_h = db.Column('timeled_open_h', db.Integer)
    timeled_open_m = db.Column('timeled_open_m', db.Integer)
    timeled_close_h = db.Column('timeled_close_h', db.Integer)
    timeled_close_m = db.Column('timeled_close_m', db.Integer)
    timedoor_open_h = db.Column('timedoor_open_h', db.Integer)
    timedoor_open_m = db.Column('timedoor_open_m', db.Integer)
    timedoor_close_h = db.Column('timedoor_close_h', db.Integer)
    timedoor_close_m = db.Column('timedoor_close_m', db.Integer)
    timenest_open_h = db.Column('timenest_open_h', db.Integer)
    timenest_open_m = db.Column('timenest_open_m', db.Integer)
    timenest_close_h = db.Column('timenest_close_h', db.Integer)
    timenest_close_m = db.Column('timenest_close_m', db.Integer)
    timeksr_open_h = db.Column('timeksr_open_h', db.Integer)
    timeksr_open_m = db.Column('timeksr_open_m', db.Integer)
    timeksr_close_h = db.Column('timeksr_close_h', db.Integer)
    timeksr_close_m = db.Column('timeksr_close_m', db.Integer)
    timeonfly_open_h = db.Column('timeonfly_open_h', db.Integer)
    timeonfly_open_m = db.Column('timeonfly_open_m', db.Integer)
    timeonfly_close_h = db.Column('timeonfly_close_h', db.Integer)
    timeonfly_close_m = db.Column('timeonfly_close_m', db.Integer)
    a_lux = db.Column('a_lux', db.Integer)
    a_hysteresis = db.Column('a_hysteresis', db.Integer)
    b_lux = db.Column('b_lux', db.Integer)
    b_hysteresis = db.Column('b_hysteresis', db.Integer)

    @property
    def serialize(self):
        t1 = self.time_sam.strftime("%m/%d/%Y, %H:%M:%S")
        t2 = self.time_con.strftime("%m/%d/%Y, %H:%M:%S")
        if t1 == "01/01/0001, 00:00:00":
            t1 = "NO TIME"
        if t2 == "01/01/0001, 00:00:00":
            t2 = "NO TIME"
        return {
            'pub_id': self.pub_id,
            'time_sam': t1,
            'time_con': t2,
            'lux': self.lux,
            'timeled_open_h': self.timeled_close_h,
            'timeled_open_m': self.timeled_open_m,
            'timeled_close_h': self.timeled_close_h,
            'timeled_close_m': self.timeled_close_m,
            'timedoor_open_h': self.timedoor_open_h,
            'timedoor_open_m': self.timedoor_open_m,
            'timedoor_close_h': self.timedoor_close_h,
            'timedoor_close_m': self.timedoor_close_m,
            'timenest_open_h': self.timenest_open_h,
            'timenest_open_m': self.timenest_open_m,
            'timenest_close_h': self.timenest_close_h,
            'timenest_close_m': self.timenest_close_m,
            'timeksr_open_h': self.timeksr_open_h,
            'timeksr_open_m': self.timeksr_open_m,
            'timeksr_close_h': self.timeksr_close_h,
            'timeksr_close_m': self.timeksr_close_m,
            'timeonfly_open_h': self.timeonfly_open_h,
            'timeonfly_open_m': self.timeonfly_open_m,
            'timeonfly_close_h': self.timeonfly_close_h,
            'timeonfly_close_m': self.timeonfly_close_m,
            'a_lux': self.a_lux,
            'a_hysteresis': self.a_hysteresis,
            'b_lux': self.b_lux,
            'b_hysteresis': self.b_hysteresis
        }

    @property
    def duplicate(self):
        return Farm(
            pub_id=self.pub_id,
            time_sam=self.time_sam,#.strftime("%m/%d/%Y, %H:%M:%S"),
            time_con=self.time_con,#.strftime("%m/%d/%Y, %H:%M:%S"),
            lux=self.lux,
            timeled_open_h=self.timeled_close_h,
            timeled_open_m=self.timeled_open_m,
            timeled_close_h=self.timeled_close_h,
            timeled_close_m=self.timeled_close_m,
            timedoor_open_h=self.timedoor_open_h,
            timedoor_open_m=self.timedoor_open_m,
            timedoor_close_h=self.timedoor_close_h,
            timedoor_close_m=self.timedoor_close_m,
            timenest_open_h=self.timenest_open_h,
            timenest_open_m=self.timenest_open_m,
            timenest_close_h=self.timenest_close_h,
            timenest_close_m=self.timenest_close_m,
            timeksr_open_h=self.timeksr_open_h,
            timeksr_open_m=self.timeksr_open_m,
            timeksr_close_h=self.timeksr_close_h,
            timeksr_close_m=self.timeksr_close_m,
            timeonfly_open_h=self.timeonfly_open_h,
            timeonfly_open_m=self.timeonfly_open_m,
            timeonfly_close_h=self.timeonfly_close_h,
            timeonfly_close_m=self.timeonfly_close_m,
            a_lux=self.a_lux,
            a_hysteresis=self.a_hysteresis,
            b_lux=self.b_lux,
            b_hysteresis=self.b_hysteresis
        )

class Session(db.Model):
    __tablename__ = 'session'
    session_id = db.Column('session_id', db.String(100), nullable=True, unique=True)  # can be crypt
    pub_id = db.Column('pub_id', db.String(100), db.ForeignKey('userfarm.pub_id'), nullable=False)
    key = db.Column('key', db.String(500))
    sid = db.Column('sid', db.String(100), nullable=True)
    otp = db.Column('otp', db.String(100), primary_key=True)
    flag = db.Column('flag', db.Boolean, nullable=True)
    time_start = db.Column('time_start', db.DateTime, nullable=True)
    time_end = db.Column('time_end', db.DateTime, nullable=True)

class UserDevice(UserMixin, db.Model):
    __tablename__ = 'userdevice'
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(100), unique=True)
    password = db.Column('password', db.String(100)) #crypt

class Motor(db.Model):
    _tablename_ = 'motor'
    motor_id = db.Column('motor_id', db.Integer, primary_key=True) #1-7
    farm_id = db.Column('farm_id', db.String(100), db.ForeignKey('farm.pub_id'), primary_key=True)
    time_sam = db.Column('time_sam', db.DateTime, db.ForeignKey('farm.time_sam'), primary_key=True)
    time_con = db.Column('time_con', db.DateTime, db.ForeignKey('farm.time_con'), primary_key=True)
    addresses = db.Column('addresses', db.String(20))
    numbers = db.Column('numbers', db.String(10))
    time_ready = db.Column('time_ready', db.Integer)
    active = db.Column('active', db.Boolean)

    @property
    def serialize(self):
        return {
            'motor_id': self.motor_id,
            'farm_id': self.farm_id,
            'addresses': self.addresses,
            'numbers': self.numbers,
            'time_ready': self.time_ready,
            'active': self.active
        }

    @property
    def duplicate(self):
        return Motor(
            motor_id=self.motor_id,
            farm_id=self.farm_id,
            time_sam=self.time_sam,  # .strftime("%m/%d/%Y, %H:%M:%S"),
            time_con=self.time_con,  # .strftime("%m/%d/%Y, %H:%M:%S"),
            addresses=self.addresses,
            numbers=self.numbers,
            time_ready=self.time_ready,
            active=self.active
        )

class Led(db.Model):
    _tablename_ = 'led'
    led_id = db.Column('led_id', db.Integer, primary_key=True) #1-6
    farm_id = db.Column('farm_id', db.String(100), db.ForeignKey('userfarm.pub_id'), primary_key=True)
    time_sam = db.Column('time_sam', db.DateTime, db.ForeignKey('farm.time_sam'), primary_key=True)
    time_con = db.Column('time_con', db.DateTime, db.ForeignKey('farm.time_con'), primary_key=True)
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
            'addresses': self.addresses,
            'numbers': self.numbers,
            'max_value': self.max_value,
            'dim_up_delay': self.dim_up_delay,
            'dim_down_delay': self.dim_down_delay,
            'dim_time': self.dim_time,
            'active': self.active
        }

    @property
    def duplicate(self):
        return Led(
            led_id=self.led_id,
            farm_id=self.farm_id,
            time_sam=self.time_sam,  # .strftime("%m/%d/%Y, %H:%M:%S"),
            time_con=self.time_con,  # .strftime("%m/%d/%Y, %H:%M:%S"),
            addresses=self.addresses,
            numbers=self.numbers,
            max_value=self.max_value,
            dim_up_delay=self.dim_up_delay,
            dim_down_delay=self.dim_down_delay,
            dim_time=self.dim_time,
            active=self.active
        )

class Change(db.Model):
    _tablename_ = 'change'
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('userdevice.user_id'), primary_key=True)
    pub_id = db.Column('pub_id', db.String(100), db.ForeignKey('userfarm.pub_id'), primary_key=True)
    dev = db.Column('dev', db.Integer)
    code = db.Column('code', db.Integer)
    val = db.Column('val', db.String(20))
    time_req = db.Column('time_req', db.DateTime, primary_key=True)
    flag = db.Column('flag', db.Boolean, default=False)