from flask import Flask,render_template,url_for,request,session,redirect,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,current_user,logout_user
from wtforms import StringField, PasswordField, SubmitField, SelectField,widgets, HiddenField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, length, InputRequired, EqualTo, Optional
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

    def __lt__(self, other):
        return self.idg<other.idg


###________________FORMULAIRES WTFORMS______________________________###

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    #peuplement des valeurs possibles des sélections,
    # nécessaires pour utilisation de validate_on_submit
    courses = Categories.query.filter_by(parent=1).all()
    courses_choices = sorted([(c.little_name,c.real_name) for c in courses])
    course = SelectField('Rubrique', choices=courses_choices)

    Id_Courses=[c.idg for c in courses]
    categories = Categories.query.filter(Categories.parent.in_(Id_Courses)).all()
    categories_choices = sorted([(c.little_name, c.real_name) for c in categories])
    category = SelectField('category', choices=[('none','None')]+categories_choices,default = 'none',validators=[Optional()])

    Id_Categories = [c.idg for c in categories]
    subcategories = Categories.query.filter(Categories.parent.in_(Id_Categories)).all()
    subcategories_choices = sorted([(c.little_name, c.real_name) for c in subcategories])
    subcategory = SelectField('subcategory', choices=[('none','None'),('new','New')]+subcategories_choices,default = 'none',validators=[Optional()])

    Images = MultipleFileField('Images')
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

    return render_template('squelette.html',cats=get_child("Root"))


@app.route('/addpost', methods=['GET','POST'])
@login_required
def add_post():
    form=PostForm()

    if form.validate_on_submit() :
        print(form.course.data)
        print(form.category.data)
        print(form.subcategory.data)
        post=BlogPost(title=form.title.data,
                      course=form.course.data,
                      category=form.category.data,
                      subcategory= form.subcategory.data,
                      content=form.content.data,
                      date=datetime.datetime.now())
        print('ok')
        db.session.add(post)
        db.session.commit()

        post=BlogPost.query.filter_by(title=form.title.data).first()
        return redirect(url_for('view_post',post_id=post.id_post))
    else :

        print("Ben non")
        print(form.course.data)
        print(form.category.data)
        print(form.subcategory.data)
        return render_template('add_post.html',form=form,cats=get_child("Root"))

@app.route('/update_addpost',methods=['POST'])
def update_addpost():
    if 'course' in request.form.keys():
        course = request.form['course']
        id_course = Categories.query.filter_by(little_name=course).first()
        print(f"{id_course.idg}")
        cats = Categories.query.filter_by(parent=id_course.idg).all()
        rep={}
        for c in cats :
            rep[c.little_name]=c.real_name
        return jsonify(rep)
    elif request.form['category'] :
        category = request.form['category']
        id_category = Categories.query.filter_by(little_name=category).first()
        subcats = Categories.query.filter_by(parent=id_category.idg).all()
        rep = {}
        for c in subcats:
            rep[c.little_name] = c.real_name
        return jsonify(rep)
    else :
        return jsonify({'error' : 'Une erreur est survenue'})
    
@app.route('/viewpost/<int:post_id>')
def view_post(post_id):
    post=BlogPost.query.filter_by(id_post=post_id).first()
    return render_template('one_post.html', post=post,cats=get_child("Root"))

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
    return render_template("login.html",form=form,cats=get_child("Root"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.template_filter('getchild')
def get_child(r) :
    parent=Categories.query.filter_by(real_name=r).first()
    cats = Categories.query.filter_by(parent=parent.idg).all()
    return [c.real_name for c in sorted(cats)]


if __name__ == '__main__':
    app.run(debug=True)
