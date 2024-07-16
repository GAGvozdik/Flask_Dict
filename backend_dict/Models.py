from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import time
import math

#TODO add data 2 DB
#TODO Связи между таблицами
#TODO навести порядок, добавить время, убрать лишние поля
db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    psw = db.Column(db.String(500), nullable=False)
    avatar = db.Column(db.LargeBinary)
    comments_numb = db.Column(db.Integer)
    time = db.Column(db.Integer, nullable=False)

    # TODO add data 2 DB
    # date = db.Column(db.DateTime, default=datetime.utcnow)

    #TODO Связи между таблицами
    # pr = db.relationship('Profiles', backref='users', uselist=False)



    @staticmethod
    def addUser(name, email, hpsw):
        try:
            # Проверяем наличие пользователя по email
            user = Users.query.filter_by(email=email).first()
            if user:
                print("Пользователь с таким email уже существует")
                return False

            # Создаем нового пользователя
            new_user = Users(name=name, email=email, psw=hpsw, comments_numb=0, time=math.floor(time.time()))
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print("addUser Ошибка добавления пользователя в БД " + str(e))
            return False

        return True

    @staticmethod
    def getUser(user_id):
        try:
            # Получаем пользователя по ID
            user = Users.query.get(user_id)
            if not user:
                print("getUser Пользователь не найден")
                return False

            return user  # Возвращаем объект User
        except Exception as e:
            print("getUser Ошибка получения данных из БД " + str(e))

        return False

    @staticmethod
    def getUserByEmail(email):
        try:
            # Получаем пользователя по email
            user = Users.query.filter_by(email=email).first()
            if not user:
                print("getUserByEmail Пользователь не найден")
                return False

            return user  # Возвращаем объект User
        except Exception as e:
            print("getUserByEmail Ошибка получения данных из БД " + str(e))

        return False

    @staticmethod
    def updateUserCommentsNumb(comments_numb, email):
        try:
            # Обновляем число комментариев пользователя
            user = Users.query.filter_by(email=email).first()
            if user:
                user.comments_numb = comments_numb
                db.session.commit()
                return True
            else:
                print("updateUserCommentsNumb Пользователь не найден")
                return False
        except Exception as e:
            print("updateUserCommentsNumb Ошибка обновления аватара в БД: " + str(e))
            return False


    @staticmethod
    def getUsersE(email):
        try:
            users = Users.query.filter_by(email=email).all()
            if users:
                return users
        except Exception as e:
            print("getUsersE Ошибка получения статьи из БД " + str(e))

        return (False, False)

    @staticmethod
    def getUsersN(name):
        try:
            users = Users.query.filter_by(name=name).all()
            if users:
                return users
        except Exception as e:
            print("getUsersN Ошибка получения статьи из БД " + str(e))

        return (False, False)

    @staticmethod
    def updatePsw(email, psw):
        try:
            user = Users.query.filter_by(email=email).first()
            if user:
                user.psw = psw
                db.session.commit()
                return True
            else:
                print("updatePsw Пользователь не найден")
                return False
        except Exception as e:
            print("updatePsw Ошибка обновления оценок мфк в БД: " + str(e))
            return False

    def __repr__(self):
        return f"<users {self.id}>"


class Mfk(db.Model):
    __tablename__ = 'mfk'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    faculty = db.Column(db.String(255))
    desc = db.Column(db.Text)
    online = db.Column(db.String(255))
    openclose = db.Column(db.Integer)
    score = db.Column(db.Integer)
    score_numb = db.Column(db.Integer)

    @staticmethod
    def getSearchMfk(a):
        try:
            # Поиск по имени, факультету и описанию
            results = db.session.query(Mfk).filter(
                Mfk.name.like(f"%{a}%") | 
                Mfk.faculty.like(f"%{a}%") | 
                Mfk.desc.like(f"%{a}%")
            ).all()

            if results:
                return results
            else:
                return False, False  # Возвращаем False, если ничего не найдено
        except Exception as e:
            print("getSearchMfk Ошибка получения статьи из БД " + str(e))
            return False, False  # Возвращаем False, если возникла ошибка

    @staticmethod
    def getMfkAnonce():
        try:
            # Получение всех записей Mfk в обратном порядке
            results = db.session.query(Mfk).order_by(Mfk.id.desc()).all()
            if results:
                return results
            else:
                return []  # Возвращаем пустой список, если ничего не найдено
        except Exception as e:
            print("getMfkAnonce Ошибка получения статей из БД " + str(e))
            return []  # Возвращаем пустой список, если возникла ошибка


    @staticmethod
    def updateMfkScoreNumb(mfk_id, score_numb):
        try:
            mfk = Mfk.query.filter_by(id=mfk_id).first()
            if mfk:
                mfk.score_numb = score_numb
                db.session.commit()
                return True
            else:
                print("updateMfkScoreNumb MFK не найден")
                return False
        except Exception as e:
            print("updateMfkScoreNumb Ошибка обновления оценок мфк в БД: " + str(e))
            return False

    @staticmethod
    def getMfkScoreNumb(mfk_id):
        try:
            mfk = Mfk.query.filter_by(id=mfk_id).first()
            if mfk:
                return mfk.score_numb
        except Exception as e:
            print("getMfkScoreNumb Ошибка получения статьи из БД " + str(e))
        return None
    

    @staticmethod
    def getMfkName(mfk_id):
        try:
            mfk = Mfk.query.filter_by(id=mfk_id).first()
            if mfk:
                return mfk.name
        except Exception as e:
            print("getMfkName Ошибка получения статьи из БД " + str(e))
        return None
    
    @staticmethod
    def updateMfkScore(mfkname, score):
        try:
            mfk = Mfk.query.filter_by(id=mfkname).first()
            if mfk:
                mfk.score = score
                db.session.commit()
                return True
            else:
                print("updateMfkScore MFK не найден")
                return False
        except Exception as e:
            print("updateMfkScore Ошибка обновления оценок мфк в БД: " + str(e))
            return False


    @staticmethod
    def getMfk(alias):
        try:
            # Получаем MFK по ID
            mfk = Mfk.query.filter_by(id=alias).first()
            if mfk:
                return mfk
        except Exception as e:
            print("getMfk Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def __repr__(self):
        return f"<Mfk {self.id}>"

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    mfkname = db.Column(db.String(255))
    score = db.Column(db.Integer, default=0)
    mfktitle = db.Column(db.String(255))
    markScore = db.Column(db.Integer, default=0)
    reason = db.Column(db.Text)

    @staticmethod
    def getMfkScore(alias):
        try:
            # Используйте sqlalchemy для запроса к базе данных
            results = db.session.query(Comments.score).filter(Comments.mfkname.like(f"%{alias}%")).all()
            if results:
                return results
        except Exception as e:
            print("getMfkScore Ошибка получения статьи из БД " + str(e))

        return []  # Возвращаем пустой список в случае ошибки


    @staticmethod
    def getComment(alias):
        try:
            # Используйте sqlalchemy для запроса к базе данных
            results = db.session.query(Comments.username, Comments.mfkname, Comments.score, Comments.reason).filter(Comments.mfkname.like(f"%{alias}%")).all()
            if results:
                return results
        except Exception as e:
            print("getComment Ошибка получения статьи из БД " + str(e))

        return []  # Возвращаем пустой список в случае ошибки

    @staticmethod
    def getUserCommentsNumb(name):
        try:
            # Получаем комментарии пользователя по имени
            comments = Comments.query.filter_by(username=name).all()  # Используйте Comments модель
            if comments:
                return comments
        except Exception as e:
            print("getUserCommentsNumb Ошибка получения статьи из БД " + str(e))

        return (False, False)

    @staticmethod
    def delComment(mfktitle, name):
        try:
            comment = Comments.query.filter_by(mfktitle=mfktitle, username=name).first()
            if comment:
                db.session.delete(comment)
                db.session.commit()
                return True
            else:
                print("delComment Комментарий не найден")
                return False
        except Exception as e:
            print("delComment Ошибка обновления оценок мфк в БД: " + str(e))
            return False


    @staticmethod
    def addComment(username, mfkname, score, mfktitle, mark_score, reason):
        try:
            new_comment = Comments(username=username, mfkname=mfkname, score=score, mfktitle=mfktitle, markScore=mark_score, reason=reason)
            db.session.add(new_comment)  # Добавляем новый комментарий в сессию
            db.session.commit()  # Сохраняем изменения в базе данных
            return True
        except Exception as e:
            print("addComment Ошибка добавления статьи в БД " + str(e))
            return False

    def __repr__(self):
        return f"<Comments {self.id}>"
    

