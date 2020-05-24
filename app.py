from flask import Flask,render_template,url_for,request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,current_user,logout_user
from wtforms import StringField, PasswordField, SubmitField, SelectField,widgets, HiddenField, TextAreaField
from wtforms.validators import DataRequired, length, InputRequired, EqualTo
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import datetime
from flaskext.markdown import Markdown

from werkzeug import security

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///static/zonensidb.sqlite3'

###________CONFIGURATION DES MODULES_____________###
db=SQLAlchemy(app)
#login_manager = LoginManager()
#login_manager.init_app(app)
Markdown(app)

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
    date=db.Column(db.DateTime)

###________________FORMULAIRES WTFORMS______________________________###


class PostForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    course = SelectField('Matière', choices=[ ('maths','Mathématiques'),
                                                        ('nsi', 'NSI'),
                                                        ('snt', 'SNT'),
                                                        ('esci', 'Ens. Sci.'),
                                                        ('misc', 'Misc')],
                        default = 'maths')
    content = TextAreaField("Contenu")

###__________________LOGIN MANAGER POUR Flask-Login____________________________###

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('squelette.html')

@app.route('/addpost', methods=['GET','POST'])
def add_post():
    form=PostForm()
    if form.validate_on_submit() :
        post=BlogPost(title=form.title.data,
                      course=form.course.data,
                      content=form.content.data,
                      date=datetime.datetime.now())
        db.session.add(post)
        db.session.commit()
        #return redirect(url_for('index'))
        post=BlogPost.query.filter_by(title=form.title.data).first()
        return redirect(url_for('view_post',post_id=post.id_post))
    else :
        return render_template('add_post.html',form=form)
    
@app.route('/viewpost/<int:post_id>')
def view_post(post_id):
    post=BlogPost.query.filter_by(id_post=post_id).first()
    return render_template('one_post.html', post=post)


if __name__ == '__main__':
    app.run(debug=True)
