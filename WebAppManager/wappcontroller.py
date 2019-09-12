from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from jose import jws
from flask_login import LoginManager, login_user, login_required, logout_user

from Db.models import db
from Db.models import UserDevice
from Db.models import UserFarm
from Db.models import Session
from Db.models import Motor
from Db.models import Led
from Db.models import Change

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost/SmartFarmPoultry'
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
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

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
    farms = UserFarm.query.all() #.order_by(Change.time_req.asc(), )
    data = []
    for farm in farms:
        if Session.query.filter_by(pub_id=farm.pub_id, flag=True).first() is not None:
            flag = True
        else:
            flag = False
        if farm.time_sam > farm.time_con:
            time = farm.time_sam
        else:
            time = farm.time_con
        data.append({'id': farm.pub_id, 'active': flag, 'last_update': time.strftime("%m/%d/%Y, %H:%M:%S")})
    return render_template('dashboard.html', data=data)

@app.route('/farm_<cod>')
@login_required
def farm(cod):
    data = []
    farm = UserFarm.query.filter_by(pub_id=cod).first()
    motors = Motor.query.filter_by(farm_id=cod).all()
    leds = Led.query.filter_by(farm_id=cod).all()
    data.append(farm.serialize)
    i = 0
    for motor in motors:
        data.append(motor.serialize)
        data[i+1]['name'] = mot_con[i]
        i = i+1
    i = 0
    for led in leds:
        data.append(led.serialize)
        data[i + 8]['name'] = le_con[i]
        i = i + 1
    print(data)
    return render_template('farm.html', data=data)

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