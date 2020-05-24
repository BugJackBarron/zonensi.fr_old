from flask import Flask,render_template,url_for,request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,current_user,logout_user
from wtforms import StringField, PasswordField, SubmitField, SelectField,widgets, HiddenField
from wtforms.validators import DataRequired, length, InputRequired, EqualTo
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import datetime

from werkzeug import security

app = Flask(__name__)
app.config['secret_key'] = 'secret'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///static/zonensidb.sqlite3'

###________CONFIGURATION DES MODULES_____________###
db=SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

###_________________CLASSES DES TABLES POUR SQLALCHEMY________________________________###
class User(UserMixin, db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)



class BlogPost(db.Model) :
    id_post = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=True)
    course = db.Column(db.String(40))
    category = db.Column(db.String(40))
    subcategory = db.Column(db.String(40))
    content = db.Column(db.Text)




@app.route('/')
def index():
    return render_template('squelette.html')


if __name__ == '__main__':
    app.run(debug=True)
