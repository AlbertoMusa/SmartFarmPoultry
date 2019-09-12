from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import InputRequired, Length, NumberRange, Optional
from jose import jws
from flask_login import LoginManager, login_user, login_required, logout_user

from Db.models2 import db
from Db.models2 import UserDevice
from Db.models2 import UserFarm
from Db.models2 import Farm
from Db.models2 import Session
from Db.models2 import Motor
from Db.models2 import Led
from Db.models2 import Change

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost/SmartFarmPoultry2'
bootstrap = Bootstrap(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

key = "key_encode"
mot_con = ["flapLeftFront", "flapLeftBack", "flapRightFront", "flapRightBack", "nestEject", "flapKsr", "onFlyPole"]
le_con = ["LEDTop", "LEDMid", "LEDBottom", "LEDNest", "LEDKsr", "LEDAlways"]

@login_manager.user_loader
def load_user(user_id):
    return UserDevice.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = wtforms.StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = wtforms.PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = wtforms.BooleanField('remember me')

class ChangeForm(FlaskForm):
    lux = wtforms.IntegerField('led off lux:', validators=[Optional(), NumberRange(min=0)])
    time_open_led = wtforms.TimeField('time open led:', validators=[Optional()])
    time_close_led = wtforms.TimeField('time close led:', validators=[Optional()])
    time_open_door = wtforms.TimeField('time open door:', validators=[Optional()])
    time_close_door = wtforms.TimeField('time close door:', validators=[Optional()])
    time_open_nest = wtforms.TimeField('time open nest:', validators=[Optional()])
    time_close_nest = wtforms.TimeField('time close nest:', validators=[Optional()])
    time_open_ksr = wtforms.TimeField('time open ksr:', validators=[Optional()])
    time_close_ksr = wtforms.TimeField('time close ksr:', validators=[Optional()])
    time_open_fly = wtforms.TimeField('time open fly:', validators=[Optional()])
    time_close_fly = wtforms.TimeField('time close fly:', validators=[Optional()])
    close_door_lux = wtforms.IntegerField('close door lux:', validators=[Optional(), NumberRange(min=0)])
    close_door_hysteresis = wtforms.IntegerField('close door hysteresis:', validators=[Optional(), NumberRange(min=0)])
    led_off_lux = wtforms.IntegerField('led off lux:', validators=[Optional(), NumberRange(min=0)])
    led_of_hysteresis = wtforms.IntegerField('led off hysteresis:', validators=[Optional(), NumberRange(min=0)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserDevice.query.filter_by(username=form.username.data).first()
        if user:
            if jws.verify(user.password, key, algorithms=['HS256']).decode() == form.password.data:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return render_template('index.html', data="Invalid username or password")
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    farms = UserFarm.query.all()
    data = []
    for f in farms:
        if Session.query.filter_by(pub_id=f.pub_id, flag=True).first() is not None:
            flag = True
        else:
            flag = False
        if Farm.query.filter_by(pub_id=f.pub_id).first() is not None:
            farm_data = Farm.query.filter_by(pub_id=f.pub_id).order_by(Farm.time_sam.desc(), Farm.time_con.desc()).first()
            if farm_data.time_sam > farm_data.time_con:
                time = farm_data.time_sam.strftime("%m/%d/%Y, %H:%M:%S")
            else:
                time = farm_data.time_con.strftime("%m/%d/%Y, %H:%M:%S")
            if time == "01/01/0001, 00:00:00":
                time = "NO TIME"
        else:
            time = "NO TIME"
        data.append({'id': f.pub_id, 'active': flag, 'last_update': time})
    return render_template('dashboard.html', data=data)

@app.route('/farm_<cod>', methods=['GET', 'POST'])
@login_required
def farm(cod):
    data = []
    form = ChangeForm()
    if form.validate_on_submit():
        print(form.close_door_hysteresis.data)
        print(form.time_open_door.data)
        return redirect(url_for('dashboard'))
    if Farm.query.filter_by(pub_id=cod).order_by(Farm.time_sam.desc(), Farm.time_con.desc()).first() is not None:
        farm = Farm.query.filter_by(pub_id=cod).order_by(Farm.time_sam.desc(), Farm.time_con.desc()).first()
        motors = Motor.query.filter_by(farm_id=cod).order_by(Motor.time_sam.desc(), Motor.time_con.desc()).limit(7).all()
        leds = Led.query.filter_by(farm_id=cod).order_by(Led.time_sam.desc(), Led.time_con.desc()).limit(6).all()
        data.append(farm.serialize)
        i = 0
        for motor in motors:
            data.append(motor.serialize)
            data[i + 1]['name'] = mot_con[i]
            i = i + 1
        i = 0
        for led in leds:
            data.append(led.serialize)
            data[i + 8]['name'] = le_con[i]
            i = i + 1
    else:
        data = 1
    return render_template('farm.html', data=data, cod=cod, form=form)

@app.route('/history')
@login_required
def history():
    farms = UserFarm.query.all()
    data = []
    for f in farms:
        if Session.query.filter_by(pub_id=f.pub_id, flag=True).first() is not None:
            flag = True
        else:
            flag = False
        if Farm.query.filter_by(pub_id=f.pub_id).first() is not None:
            farm_data = Farm.query.filter_by(pub_id=f.pub_id).order_by(Farm.time_sam.desc(), Farm.time_con.desc()).first()
            if farm_data.time_sam > farm_data.time_con:
                time = farm_data.time_sam.strftime("%m/%d/%Y, %H:%M:%S")
            else:
                time = farm_data.time_con.strftime("%m/%d/%Y, %H:%M:%S")
            if time == "01/01/0001, 00:00:00":
                time = "NO TIME"
        else:
            time = "NO TIME"
        data.append({'id': f.pub_id, 'active': flag, 'last_update': time})
    return render_template('history.html', data=data)

@app.route('/history_<cod>')
@login_required
def history_farms(cod):
    data = []
    n = 0
    if Farm.query.filter_by(pub_id=cod).first() is not None:
        farms = Farm.query.filter_by(pub_id=cod).order_by(Farm.time_sam.desc(), Farm.time_con.desc())
        for f in farms:
            time1 = f.time_sam.strftime("%m/%d/%Y, %H:%M:%S")
            time2 = f.time_con.strftime("%m/%d/%Y, %H:%M:%S")
            if time1 == "01/01/0001, 00:00:00":
                time1 = "NO TIME"
            if time2 == "01/01/0001, 00:00:00":
                time2 = "NO TIME"
            n = n+1
            data.append({'time1': time1, 'time2': time2})
    else:
        data = 1
    return render_template('farm_history.html', data=data, id=cod, n=n)

@app.route('/history_<cod><n>')
@login_required
def history_farm(cod, n):
    data = []
    farm = Farm.query.filter_by(pub_id=cod).order_by(Farm.time_sam.asc(), Farm.time_con.asc()).limit(n).all()
    motors = Motor.query.filter_by(farm_id=cod, time_sam=farm[int(n)-1].time_sam, time_con=farm[int(n)-1].time_con).order_by(Motor.time_sam.desc(), Motor.time_con.desc()).limit(7).all()
    leds = Led.query.filter_by(farm_id=cod, time_sam=farm[int(n)-1].time_sam, time_con=farm[int(n)-1].time_con).order_by(Led.time_sam.desc(), Led.time_con.desc()).limit(6).all()
    data.append(farm[int(n)-1].serialize)
    i = 0
    for motor in motors:
        data.append(motor.serialize)
        data[i + 1]['name'] = mot_con[i]
        i = i + 1
    i = 0
    for led in leds:
        data.append(led.serialize)
        data[i + 8]['name'] = le_con[i]
        i = i + 1
    return render_template('farm_history_details.html', data=data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#def main():
    #app.run(debug=True, host='127.0.0.1', port=5001)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
    #main()