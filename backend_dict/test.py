import numpy as np
import sqlite3
import math
import time

# file = open("mfk_list.txt", "r", encoding="utf-8")
#
# mfk_list = []
#
# for line in file:
#     if len(line.split('\t')) == 4:
#         mfk_list.append(np.array(line.split('\t')))
# mfk_list = np.array(mfk_list)
#

# tm = math.floor(time.time())

def insert_varible_into_table(name, faculty, desc, online, openclose, score):
    try:

        sqlite_connection = sqlite3.connect('flsite.db')
        cursor = sqlite_connection.cursor()

        sqlite_insert_with_param = """INSERT INTO mfk
                              (name, faculty, desc, online, openclose, score)
                              VALUES (?, ?, ?, ?, ?, ?);"""

        data_tuple = (name, faculty, desc, online, openclose, score)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def read_table(db):
    try:

        sqlite_connection = sqlite3.connect(db)
        cursor = sqlite_connection.cursor()

        sqlite_insert_with_param = "SELECT * FROM course"


        cursor.execute(sqlite_insert_with_param)
        sqlite_connection.commit()
        # print("Переменные Python успешно вставлены в таблицу")
        return cursor.fetchall()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def add_mfk_to_db():

    mfk_list=read_table("data.db")

    for i in range(len(mfk_list)):
        tm = math.floor(time.time())
        tm = math.floor(time.time())
        insert_varible_into_table(mfk_list[i][0], mfk_list[i][1], mfk_list[i][2], "", "", "0")


def del_db():
    conn = sqlite3.connect('flsite.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS comments')
    conn.commit()
    cursor.execute('DROP TABLE IF EXISTS users')
    conn.commit()
    cursor.execute('DROP TABLE IF EXISTS mfk')

    conn.commit()
    conn.close()
# del_db()

from mainApp import db
db.create_all()

















































