from flask import Flask,render_template,url_for,request,session,redirect,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm

from flask_login import LoginManager,UserMixin,login_user,login_required,current_user,logout_user
from wtforms import StringField, PasswordField, SubmitField, SelectField,widgets, HiddenField, TextAreaField, MultipleFileField, FieldList
from wtforms.validators import DataRequired, length, InputRequired, EqualTo, Optional, ValidationError
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
import datetime, re
from flaskext.markdown import Markdown
import os


from werkzeug import security, secure_filename



import config_app

app = Flask(__name__)
app.config['SECRET_KEY'] = config_app.secret_key
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = config_app.bdd_file

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
    tags = db.Column(db.Text)


class Categories(db.Model) :
    little_name = db.Column(db.String(10))
    real_name = db.Column(db.String(40))
    parent = db.Column(db.Integer)
    idg = db.Column(db.Integer,primary_key=True)
    idd = db.Column(db.Integer,primary_key=True)
    isactive = db.Column(db.Boolean,default=True)
    def __lt__(self, other):
        return self.idg<other.idg


class Quizz(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(40))
    nbItems = db.Column(db.Integer)
    items = db.Column(db.Text)
    categories = db.Column(db.Text)
    tags = db.Column(db.Text)


class QuizzItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    propositions = db.Column(db.Text)
    valideProps = db.Column(db.String(40))
    image = db.Column(db.String(40))
    categories = db.Column(db.Text)

###________________FORMULAIRES WTFORMS______________________________###

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(FlaskForm):
    #########################################################
    # Classe à désactiver si relance de la création de la   #
    # BDD                                                   #
    #########################################################
    title = StringField('Titre', validators=[DataRequired()])
    #peuplement des valeurs possibles des sélections,
    # nécessaires pour utilisation de validate_on_submit
    courses = Categories.query.filter_by(parent=1).all()
    courses_choices = sorted([(c.little_name,c.real_name) for c in courses if c.isactive])
    course = SelectField('Rubrique', choices=courses_choices)

    Id_Courses=[c.idg for c in courses]
    categories = Categories.query.filter(Categories.parent.in_(Id_Courses)).all()
    categories_choices = sorted([(c.little_name, c.real_name) for c in categories if c.isactive])
    category = SelectField('category', choices=[('none','None')]+categories_choices,default = 'none',validators=[Optional()])

    Id_Categories = [c.idg for c in categories]
    subcategories = Categories.query.filter(Categories.parent.in_(Id_Categories)).all()
    subcategories_choices = sorted([(c.little_name, c.real_name) for c in subcategories if c.isactive ])
    subcategory = SelectField('subcategory', choices=[('none','None')]+subcategories_choices,default = 'none',validators=[Optional()])

    Images = MultipleFileField('Images')
    content = TextAreaField("Contenu")

    def validate_title(form,field):
        if BlogPost.query.filter_by(title=field.data).first() != None :
            raise ValidationError("Le titre a déjà été utilisé !")

    def validate_content(form,field):
        link_pattern = r'\[(.*?)\]\((.*?)\)'
        url_pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        pattern_image = re.findall(link_pattern, form.content.data)
        uploaded_files =[f.filename for f in form.Images.data]
        for rep in pattern_image :
            truerep = rep[1]
            if (re.search(url_pattern, truerep) is None) and (truerep not in uploaded_files) :
                raise ValidationError('Un fichier est manquant')


class CreateQuizz(FlaskForm) :
    title = StringField('Titre', validators=[DataRequired()])
    itemList = FieldList(StringField())
    submit = SubmitField('Submit')


###____________________MODIFICATIONS DES VUES DE L'ADMIN POUR Flask-Admin_______________________###


class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.login == 'admin'
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


class MyModelView(ModelView):

    can_view_details = True
    column_display_pk = True

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.login == 'admin'
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(BlogPost, db.session))
admin.add_view(MyModelView(Categories, db.session))
admin.add_view(MyModelView(Quizz, db.session))
admin.add_view(MyModelView(QuizzItems, db.session))
path = os.path.join(os.path.dirname(__file__), 'static')
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))


###__________________LOGIN MANAGER POUR Flask-Login____________________________###

@login_manager.user_loader
def load_user(id):
     return User.query.get(int(id))

##__________________________GESTION DES ERREURS___________________##

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html',cats=get_child("Root")), 404





@app.template_filter('getchild')
def get_child(r) :
    parent=Categories.query.filter_by(real_name=r).first()
    cats = Categories.query.filter_by(parent=parent.idg).all()
    return [c.real_name for c in sorted(cats) if c.isactive]


def format_markdown_links(form) :
    link_pattern = r'\[(.*?)\]\((.*?)\)'
    url_pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    pattern_image = re.findall(link_pattern,form.content.data)
    new_content=form.content.data
    for rep in pattern_image :
        print(f"found pattern {rep[1]}")
        truerep=rep[1]
        if re.search(url_pattern, truerep) is None:
            print("Not a url")
            path_to_save = f'../static/upload/{form.course.data}'
            if form.category.data != 'none':
                path_to_save += "/" + form.category.data
                if form.subcategory.data != 'none':
                    path_to_save += "/" + form.subcategory.data
            print("New path done !")
            new_content = re.sub(rep[1],path_to_save+"/"+rep[1], new_content)
    return new_content


##_________________                    __ROUTES_____________________________________##

@app.route('/')
def index():
    return render_template('squelette.html',cats=get_child("Root"))


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

@app.route('/addpost', methods=['GET','POST'])
@login_required
def add_post():
    # Formulaire d'ajout de Post
    form=PostForm()
    print(form.errors)
    if form.validate_on_submit() :
        post=BlogPost(title=form.title.data,
                      course=form.course.data,
                      category=form.category.data,
                      subcategory= form.subcategory.data,
                      content=format_markdown_links(form),
                      date=datetime.datetime.now())
        for file in form.Images.data :
            if file.filename != '' :
                filename = secure_filename(file.filename)
                path_to_save=f'static/upload/{form.course.data}'
                if form.category.data != 'none' :
                    path_to_save+="/"+form.category.data
                    if form.subcategory.data != 'none' :
                        path_to_save += "/"+form.subcategory.data
                file.save(path_to_save+"/"+filename)
        db.session.add(post)
        db.session.commit()
        post=BlogPost.query.filter_by(title=form.title.data).first()

        return redirect(url_for('view_post',post_id=post.id_post))

    else :
        return render_template('add_post.html',form=form,cats=get_child("Root"))

@app.route('/update_addpost',methods=['POST'])
@login_required
def update_addpost():
    if 'category' not in request.form.keys() and 'course' in request.form.keys() :
        course = request.form['course']
        id_course = Categories.query.filter_by(little_name=course).first()
        cats = Categories.query.filter_by(parent=id_course.idg).all()
        rep={}
        for c in cats :
            if c.isactive :
                rep[c.little_name]=c.real_name
        return jsonify(rep)
    elif request.form['category'] :
        course = request.form['course']
        category = request.form['category']
        id_course = Categories.query.filter_by(little_name=course).first().idg
        id_category = Categories.query.filter_by(little_name=category,parent=id_course).first()

        subcats = Categories.query.filter_by(parent=id_category.idg).all()
        rep = {}
        for c in subcats:
            if c.isactive :
                rep[c.little_name] = c.real_name
        return jsonify(rep)
    else :
        return jsonify({'error' : 'Une erreur est survenue'})





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_quizz',methods=['GET','POST'])
@login_required
def add_quizz():
    form = CreateQuizz()
    return render_template("add_quizz.html", form=form,cats=get_child("Root"))




if __name__ == '__main__':
    app.run(debug=True)
