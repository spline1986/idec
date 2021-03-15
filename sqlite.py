from base import Base
from base64 import urlsafe_b64decode
from typing import Dict, List
import sqlite3


class Sqlite(Base):

    def __init__(self, path: str):
        super().__init__(path)
        self.path = path
        self.check_base()

    def __connect(self):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        return connection, cursor

    def check_base(self):
        connection, cursor = self.__connect()
        sql = """CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        msgid TEXT,
        tags TEXT,
        echoarea TEXT,
        date INTEGER,
        msgfrom TEXT,
        address TEXT,
        msgto TEXT,
        subject TEXT,
        body TEXT,
        UNIQUE(id));"""
        cursor.execute(sql)
        connection.commit()
        connection.close()

    def get_counts(self, echoareas: List) -> Dict:
        counts = {}
        sql = "SELECT COUNT(1) FROM messages WHERE echoarea = ?;"
        connection, cursor = self.__connect()
        for echoarea in echoareas:
            count = int(cursor.execute(sql, (echoarea,)).fetchone()[0])
            counts[echoarea] = count
        connection.close()
        return counts

    def get_index(self, echoareas: List) -> List:
        index = []
        sql = "SELECT msgid FROM messages WHERE echoarea = ?;"
        connection, cursor = self.__connect()
        for echoarea in echoareas:
            index = index + list(cursor.execute(sql, (echoarea,)).fetchall())
        connection.close()
        return index

    def is_message_exists(self, echoarea: str, msgid: str) -> bool:
        connection, cursor = self.__connect()
        sql = "SELECT COUNT(1) FROM messages WHERE msgid = ?;"
        count = cursor.execute(sql, (msgid,)).fetchone()[0]
        connection.close()
        if count == 0:
            return False
        else:
            return True

    def get_message(self, msgid: str) -> str:
        connection, cursor = self.__connect()
        sql = "SELECT * FROM messages WHERE msgid = ?;"
        message = cursor.execute(sql, (msgid,)).fetchone()[0]
        connection.close()
        return "{}\n{}\n{}\n{}\n{}\n{}\n{}\n\n{}".format(*message[2:])

    def save_message(self, echoarea: str, msgid: str, message: str, cursor: object = None):
        sql = """INSERT INTO messages (msgid, tags, echoarea, date, msgfrom, address, msgto, subject, body)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        lines = message.split("\n")
        cursor.execute(sql, (msgid, *lines[:7], "\n".join(lines[8:])))

    def save_messages(self, bundle: List):
        connection, cursor = self.__connect()
        for message in bundle:
            body = urlsafe_b64decode(message["encoded"]).decode("utf-8")
            echoarea = body.split("\n")[1]
            self.save_message(echoarea, message["msgid"], body, cursor)
        connection.commit()
        connection.close()

    def toss_message(self, point: Dict, encoded: str) -> str:
        return super().toss_message(self.save_message, point, encoded)
