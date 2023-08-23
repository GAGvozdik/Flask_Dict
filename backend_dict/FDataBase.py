import sqlite3
import math
import time


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?, ?)", (name, email, hpsw, 0, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("addUser Ошибка добавления пользователя в БД " + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("getUser Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("getUser Ошибка получения данных из БД " + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("getUserByEmail Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("getUserByEmail Ошибка получения данных из БД " + str(e))
        return False

    def updateUserCommentsNumb(self, comments_numb, email):
        try:
            self.__cur.execute(f"UPDATE users SET comments_numb = ? WHERE email = ?", (comments_numb, email))
            self.__db.commit()
        except sqlite3.Error as e:
            print("updateUserCommentsNumb Ошибка обновления аватара в БД: " + str(e))
            return False
        return True

    def getUserCommentsNumb(self, name):
        try:
            self.__cur.execute(f"SELECT * FROM comments WHERE username LIKE '{name}'")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("getUserCommentsNumb Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def getMfk(self, alias):
        try:
            self.__cur.execute(f"SELECT name, faculty, desc, online FROM mfk WHERE id LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("getMfk Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def getMfkAnonce(self):
        try:
            self.__cur.execute(f"SELECT * FROM mfk ORDER BY id DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("getMfkAnonce Ошибка получения статьи из БД " + str(e))

        return []


    def addComment(self, username, mfkname, score, mfktitle, reason):
        try:

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO comments VALUES(NULL, ?, ?, ?, ?, ?)", (username, mfkname, score, mfktitle, reason))
            self.__db.commit()
        except sqlite3.Error as e:
            print("addComment Ошибка добавления статьи в БД " + str(e))
            return False

        return True

    def getComment(self, alias):
        try:
            self.__cur.execute(f"SELECT username, mfkname, score, reason FROM comments WHERE mfkname LIKE {alias}")
            # self.__cur.execute(f"SELECT * FROM comments")
            # self.__cur.execute("SELECT * FROM comments")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("getComment Ошибка получения статьи из БД " + str(e))

        return ()

    def getMfkScore(self, alias):
        try:
            self.__cur.execute(f"SELECT score FROM comments WHERE mfkname LIKE {alias}")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("getMfkScore Ошибка получения статьи из БД " + str(e))

        return ()


    def updateMfkScore(self, mfkname, score):
        try:
            self.__cur.execute(f"UPDATE mfk SET score = ? WHERE id = ?", (score, mfkname))
            self.__db.commit()
        except sqlite3.Error as e:
            print("updateMfkScore Ошибка обновления оценок мфк в БД: " + str(e))
            return False
        return True

    def getUsersE(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("getUsersE Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def getUsersN(self, name):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE name LIKE '{name}'")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("getUsersN Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def updatePsw(self, email, psw):
        try:
            self.__cur.execute(f"UPDATE users SET psw = ? WHERE email = ?", (psw, email))
            self.__db.commit()
        except sqlite3.Error as e:
            print("updatePsw Ошибка обновления оценок мфк в БД: " + str(e))
            return False
        return True

    def getSearchMfk(self, a):
        try:
            self.__cur.execute(f"SELECT * FROM mfk WHERE name LIKE '{('%' + a + '%')}' OR faculty LIKE '{('%' + a + '%')}' OR desc LIKE '{('%' + a + '%')}'")

            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("getSearchMfk Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def delComment(self, mfktitle, name):
        try:
            self.__cur.execute(f"DELETE FROM comments WHERE mfktitle = '{mfktitle}' AND username = '{name}'")

            self.__db.commit()
        except sqlite3.Error as e:
            print("delComment Ошибка обновления оценок мфк в БД: " + str(e))
            return False
        return True


    def updateMfkScoreNumb(self, mfk_id, score_numb):
        try:
            self.__cur.execute(f"UPDATE mfk SET score_numb = ? WHERE id = ?", (score_numb, mfk_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("updateMfkScoreNumb Ошибка обновления оценок мфк в БД: " + str(e))
            return False
        return True

    def getMfkScoreNumb(self, mfk_id):
        try:
            self.__cur.execute(f"SELECT score_numb FROM mfk WHERE id LIKE {mfk_id}")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("getMfkScoreNumb Ошибка получения статьи из БД " + str(e))
        return ()




























