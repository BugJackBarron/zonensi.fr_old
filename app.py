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
login_manager = LoginManager()
login_manager.init_app(app)
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


class Categories(db.Model) :
    little_name = db.Column(db.String(10))
    real_name = db.Column(db.String(40))
    parent = db.Column(db.Integer)
    idg = db.Column(db.Integer,primary_key=True)
    idd = db.Column(db.Integer,primary_key=True)


###________________FORMULAIRES WTFORMS______________________________###

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    course = SelectField('Matière', choices=[ ('maths','Mathématiques'),
                                                        ('nsi', 'NSI'),
                                                        ('snt', 'SNT'),
                                                        ('esci', 'Ens. Sci.'),
                                                        ('misc', 'Misc')],
                        default = 'maths')
    #category = SelectField('category', choices=[])
    #subcategory = SelectField('chapter', choices=[('new','New')])
    content = TextAreaField("Contenu")


###____________________MODIFICATIONS DES VUES DE L'ADMIN POUR Flask-Admin_______________________###




class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.login == 'admin'
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(BlogPost, db.session))
admin.add_view(ModelView(Categories, db.session))


###__________________LOGIN MANAGER POUR Flask-Login____________________________###

@login_manager.user_loader
def load_user(id):
     return User.query.get(int(id))

@app.route('/')
def index():

    return render_template('squelette.html')


@app.route('/addpost', methods=['GET','POST'])
@login_required
def add_post():
    form=PostForm()
    print("par la")
    if form.validate_on_submit() :
        post=BlogPost(title=form.title.data,
                      course=form.course.data,
                      content=form.content.data,
                      date=datetime.datetime.now())
        print('ok')
        db.session.add(post)
        db.session.commit()
        #return redirect(url_for('index'))
        post=BlogPost.query.filter_by(title=form.title.data).first()
        return redirect(url_for('view_post',post_id=post.id_post))
    else :
        print("Ben non")
        return render_template('add_post.html',form=form)

@app.route('/update_addpost',methods=['POST'])
def update_addpost():
    if request.form['course'] :
        course=request.form['course']

    
@app.route('/viewpost/<int:post_id>')
def view_post(post_id):
    post=BlogPost.query.filter_by(id_post=post_id).first()
    return render_template('one_post.html', post=post)

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit() :
        user = User.query.filter_by(login=form.login.data).first()
        if user :
            if user.password==form.password.data :
                login_user(user)
                if current_user.login=="admin" :
                    return redirect(url_for('admin.index'))
                else :
                    return redirect(url_for('index'))
            flash(u'La combinaison login/mot de passe est inconnue!')
    return render_template("login.html",form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
