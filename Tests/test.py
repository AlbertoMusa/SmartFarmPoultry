from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost/prova'

db = SQLAlchemy(app)

class Userr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<Userr %r>' % self.name

@app.route('/<name>')
def index(name):
    user = Userr(id=3, name=name)
    db.session.add(user)
    db.session.commit()
    return '<h1>Added New User!</h1>'

@app.route('/')
def get_user():
    user = Userr.query.first()
    print(user.id)
    #return '<h1>The user is located in: </h1>'
    return f'<h1>The user is located in: {user.id} </h1>'

    # try:
    #    UserFarm.query.filter_by(pub_id=req['pub_id'])
    #    print('SI')
    # except:
    #    print('NO')         db.session.rollback()