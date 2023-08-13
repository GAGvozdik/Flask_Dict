import numpy as np
import sqlite3
import math
import time

file = open("mfk_list.txt", "r", encoding="utf-8")

mfk_list = []

for line in file:
    # print(line.split('\t'))
    if len(line.split('\t')) == 4:
        mfk_list.append(np.array(line.split('\t')))

mfk_list = np.array(mfk_list)

# tm = math.floor(time.time())
# self.__cur.execute("INSERT INTO mfk VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)", (name, faculty, online, openclose, score, url, tm))
# self.__cur.execute("INSERT INTO mfk VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, faculty, online, openclose, discribe, teachers, whereis, whenis, complexity, semester, record, score, url, tm))


def insert_varible_into_table(name, faculty, online, openclose, score):
    try:

        sqlite_connection = sqlite3.connect('flsite.db')
        cursor = sqlite_connection.cursor()

        sqlite_insert_with_param = """INSERT INTO mfk
                              (name, faculty, online, openclose, score)
                              VALUES (?, ?, ?, ?, ?);"""

        data_tuple = (name, faculty, online, openclose, score)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()

for i in range(len(mfk_list)):
    tm = math.floor(time.time())
    tm = math.floor(time.time())
    insert_varible_into_table(mfk_list[:,0][i], mfk_list[:,1][i], mfk_list[:,2][i], mfk_list[:,3][i], "0")


























































