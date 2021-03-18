"""
Message sqlite3-base.
"""

from base.base import Base
from base64 import urlsafe_b64decode
from typing import Dict, List
import sqlite3


class Sqlite(Base):

    def __init__(self, path: str):
        super().__init__(path)
        self.path = path
        self.check_base()

    def __connect(self):
        """
        Connect to database.
        """
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        return connection, cursor

    def check_base(self):
        """
        Checks base and create this if not exists.
        """
        connection, cursor = self.__connect()
        sql = """CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        msgid TEXT,
        blacklisted INTEGER DEFAULT 0,
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
        sql = """CREATE TABLE IF NOT EXISTS points(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT,
        authstr TEXT,
        UNIQUE(id));"""
        cursor.execute(sql)
        connection.commit()
        connection.close()

    def get_blacklist(self) -> List:
        """
        Return blacklisted msgids.

        Return:
            List: List of blacklisted msgids.
        """
        connection, cursor = self.__connect()
        sql = "SELECT msgid FROM messages WHERE blacklisted = 1;"
        response = cursor.execute(sql).fetchall()
        blacklist = []
        for item in response:
            blacklist.append(item[0])
        return blacklist

    def get_counts(self, echoareas: List) -> Dict:
        """
        Counts the number of messages in a echoarea.

        Args:
            echoareas (List): Echoareas names.

        Return:
            Dict: Dict of echoareas counts (str) {"name": int}.
        """
        counts = {}
        sql = "SELECT COUNT(1) FROM messages WHERE echoarea = ?;"
        connection, cursor = self.__connect()
        for echoarea in echoareas:
            count = int(cursor.execute(sql, (echoarea,)).fetchone()[0])
            counts[echoarea] = count
        connection.close()
        return counts

    def get_index(self, echoareas: List) -> List:
        """
        Get msgids of echoareas and return they.

        Args:
            echoareas (List): Echoareas names.

        Return:
            List: Msgids.
        """
        index = []
        sql = "SELECT msgid FROM messages WHERE echoarea = ?;"
        connection, cursor = self.__connect()
        for echoarea in echoareas:
            for msgid in cursor.execute(sql, (echoarea,)).fetchall():
                index.append(msgid[0])
        connection.close()
        return index

    def is_message_exists(self, msgid: str) -> bool:
        """
        Check message exists in echoarea.

        Args:
            msgid (str): Msgid of message.

        Return:
             bool: True if message exists.
        """
        connection, cursor = self.__connect()
        sql = "SELECT COUNT(1) FROM messages WHERE msgid = ?;"
        count = cursor.execute(sql, (msgid,)).fetchone()[0]
        connection.close()
        if count == 0:
            return False
        else:
            return True

    def get_message(self, msgid: str) -> str:
        """
        Get message by msgid.

        Args:
            msgid (str): Msgid.

        Return:
            str: Message as plain text.
        """
        connection, cursor = self.__connect()
        sql = "SELECT tags, echoarea, date, msgfrom, address, msgto, " + \
              "subject, body FROM messages WHERE msgid = ?;"
        message = cursor.execute(sql, (msgid,)).fetchone()
        connection.close()
        return "{}\n{}\n{}\n{}\n{}\n{}\n{}\n\n{}".format(*message)

    def save_message(self, echoarea: str, msgid: str, message: str, cursor: object = None):
        """
        Save message to base.

        Args:
            echoarea (str): Echoarea name.
            msgid (str): Msgid.
            message (str): Message as plain text.
            cursor (object): Additional argument.

        Return:
            bool: Save status. True if message saved else False.
        """
        sql = """INSERT INTO messages (msgid, tags, echoarea, date, msgfrom, address, msgto, subject, body)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        lines = message.split("\n")
        cursor.execute(sql, (msgid, *lines[:7], "\n".join(lines[8:])))

    def save_messages(self, bundle: List) -> int:
        """
        Save messages of bundle to base.

        Args:
            bundle (List): Bundle as List of dict:
                           {"msgid", "encoded"}.

        Return:
            int: Saved messages count.
        """
        connection, cursor = self.__connect()
        new_messages = []
        echoarea = ""
        for message in bundle:
            body = urlsafe_b64decode(message["encoded"]).decode("utf-8")
            echoarea = body.split("\n")[1]
            if not self.is_message_exists(message["msgid"]):
                new_messages.append({"msgid": message["msgid"], "body": body})
        for message in new_messages:
            self.save_message(echoarea, message["msgid"], message["body"], cursor)
        connection.commit()
        connection.close()
        return len(new_messages)

    def toss_message(self, point: Dict, encoded: str) -> str:
        """
        Toss message from point and save that to base.

        Args:
            point (Dict): Point information as Dict:
                          {"name", "address"}.
            encoded (str): Point's message as plain text.

        Return:
            str: Status of tossed message:
                 "msg ok:<msgid>" or "error: msg big!".
        """
        return super().toss_message(self.save_message, point, encoded)

    def add_point(self, username: str) -> str:
        """
        Register point.

        Args:
            username (str): Point username.

        Return:
            str: Authstr.
        """
        connection, cursor = self.__connect()
        sql = "SELECT COUNT(1) FROM points WHERE username = ?"
        if cursor.execute(sql, (username,)).fetchone()[0] == 0:
            point_exists = False
        else:
            point_exists = True
        if not point_exists:
            authstr = Base.generate_authstr(username)
            sql = "INSERT INTO points (username, authstr) VALUES (?, ?);"
            cursor.execute(sql, (username, authstr))
            connection.commit()
            connection.close()
            return authstr
        return ""

    def check_point(self, authstr: str) -> Dict:
        """
        Check for a point.

        Args:
            authstr (str): Search authstr.

        Return:
            Dict: Point informationa:
                  {"name", "address"} or None.
        """
        connection, cursor = self.__connect()
        sql = "SELECT username, id FROM points WHERE authstr = ?;"
        point = cursor.execute(sql, (authstr, )).fetchone()
        if point:
            return {"name": point[0], "address": point[1]}
        return None

    def point_list(self) -> List:
        connection, cursor = self.__connect()
        sql = "SELECT username FROM points;"
        points = cursor.execute(sql).fetchall()
        usernames = []
        for point in points:
            usernames.append(point[0])
        return usernames
