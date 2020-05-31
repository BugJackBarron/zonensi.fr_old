from app import db, User, Categories
import os


if os.path.exists('static/zonensidb.sqlite3'):
    os.remove('static/zonensidb.sqlite3')
db.create_all()
user = User(login="admin", password='1234')
db.session.add(user)
db.session.commit()
racine = Categories(little_name='root', real_name='Root', parent=None, idg=1, idd=2)
db.session.add(racine)

db.session.commit()


def add_category(little_name, real_name, parent=1):
    father=Categories.query.filter_by(idg=parent).first()
    categories = Categories.query.all()
    for c in categories:
        if c.idg > father.idg: c.idg += 2
        if c.idd > father.idg: c.idd += 2
        if c.parent !=None and c.parent> father.idg : c.parent+=2
        db.session.commit()
    db.session.add(
        Categories(little_name=little_name, real_name=real_name, parent=parent, idg=parent + 1, idd=parent + 2))
    db.session.commit()


course = [('maths', 'Mathématiques'), ('snt', 'SNT'), ('nsi', 'NSI'), ('enssci', 'Enseignement Scientifique'),
          ('misc', 'Miscellanées')]

for ln, rn in course[::-1]:
    add_category(ln, rn)
    if not (os.path.exists(f"static/upload/{ln}")):
        try:
            os.mkdir(f"static/upload/{ln}")
        except:
            raise IOError

num = Categories.query.filter_by(little_name="maths").first().idg
cat = [('2de', 'Seconde'), ('1ereG', 'Première Générale'), ('TleG', 'Terminale Générale'),
       ('1ereT', 'Première Technologique'),
       ('TleT', 'Terminale Technologique'), ('mathexp', 'Maths Expertes'), ('mathcomp', 'Maths Complémentaires'),
       ('cultmath', 'Culture Mathématique')]
for ln, rn in cat[::-1]:
    add_category(ln, rn, parent=num)
    if not (os.path.exists(f"static/upload/maths/{ln}")):
        try:
            os.mkdir(f"static/upload/maths/{ln}")
        except:
            raise IOError

num = Categories.query.filter_by(little_name="nsi").first().idg
cat = [('1ereG', 'Première Générale'), ('TleG', 'Terminale Générale'), ('cultinfo', 'Culture Informatique')]
for ln, rn in cat[::-1]:
    add_category(ln, rn, parent=num)
    if not (os.path.exists(f"static/upload/nsi/{ln}")):
        try:
            os.mkdir(f"static/upload/nsi/{ln}")
        except:
            raise IOError

num = Categories.query.filter_by(little_name="misc").first().idg
cat = [('python', 'Python'), ('web', 'Web'), ('reseaux', 'Réseaux'),('linux','Linux')]
for ln, rn in cat[::-1]:
    add_category(ln, rn, parent=num)
    if not (os.path.exists(f"static/upload/misc/{ln}")):
        try:
            os.mkdir(f"static/upload/misc/{ln}")
        except:
            raise IOError


num = Categories.query.filter_by(little_name="2de").first().idg
cat = [('C01', 'C01'), ('C02', 'C02'), ('C03', 'C03')]
for ln, rn in cat[::-1]:
    add_category(ln, rn, parent=num)
    if not (os.path.exists(f"static/upload/maths/2de/{ln}")):
        try:
            os.mkdir(f"static/upload/maths/2de/{ln}")
        except:
            raise IOError


def find_children(idg):
    return Categories.query.filter_by(parent=idg).order_by(Categories.idg).all()