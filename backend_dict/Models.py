from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

#TODO add data 2 DB
#TODO Связи между таблицами

db = SQLAlchemy()

#TODO use SQLAlchemy
def create_db():
    db.create_all()





class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    psw = db.Column(db.String(500), nullable=False)

    avatar = db.Column(db.LargeBinary, nullable=True)  # Для хранения BLOB данных
    comments_numb = db.Column(db.Integer, nullable=True)
    time = db.Column(db.Integer, nullable=False)  # Возможно, используйте db.DateTime?

    # TODO add data 2 DB
    # date = db.Column(db.DateTime, default=datetime.utcnow)

    #TODO Связи между таблицами
    # pr = db.relationship('Profiles', backref='users', uselist=False)

    def __repr__(self):
        return f"<users {self.id}>"


class Mfk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    faculty = db.Column(db.String(255), nullable=True)
    desc = db.Column(db.Text, nullable=True)
    online = db.Column(db.String(255), nullable=True)
    openclose = db.Column(db.String(255), nullable=True)
    score = db.Column(db.String(255), nullable=True)
    score_numb = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Mfk {self.id}>"


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=True)
    mfkname = db.Column(db.String(255), nullable=True)
    score = db.Column(db.String(255), nullable=True)
    mfktitle = db.Column(db.String(255), nullable=True)
    reason = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Comments {self.id}>"