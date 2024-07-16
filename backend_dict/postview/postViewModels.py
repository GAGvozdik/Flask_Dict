from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import time
import math

#TODO add data 2 DB
#TODO Связи между таблицами

db = SQLAlchemy()

class Mfk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    faculty = db.Column(db.String(255), nullable=True)
    desc = db.Column(db.Text, nullable=True)
    online = db.Column(db.String(255), nullable=True)
    openclose = db.Column(db.String(255), nullable=True)
    score = db.Column(db.String(255), nullable=True)
    score_numb = db.Column(db.Integer, nullable=True)


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
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=True)
    mfkname = db.Column(db.String(255), nullable=True)
    score = db.Column(db.String(255), nullable=True)
    mfktitle = db.Column(db.String(255), nullable=True)
    reason = db.Column(db.Text, nullable=True)


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
    def addComment(username, mfkname, score, mfktitle, reason):
        try:
            new_comment = Comments(username=username, mfkname=mfkname, score=score, mfktitle=mfktitle, reason=reason)
            db.session.add(new_comment)
            db.session.commit()
        except Exception as e:
            print("addComment Ошибка добавления статьи в БД " + str(e))
            return False

        return True

    def __repr__(self):
        return f"<Comments {self.id}>"
    

