"""
Messages base based on plain text files.
"""

from base.base import Base
from base64 import urlsafe_b64decode
from os import path, mkdir
from typing import Dict, List


class Txt(Base):
    def __init__(self, path: str):
        super().__init__(path)
        if path.endswith("/"):
            self.path = path
        else:
            self.path = path + "/"
        self.check_base()

    def check_base(self):
        """
        Checks base and create this if not exists.
        """
        if not path.exists(self.path + "msg"):
            mkdir(self.path + "msg")
        if not path.exists(self.path + "echo"):
            mkdir(self.path + "echo")
        if not path.exists(self.path + "blacklist.txt"):
            open(self.path + "blacklist.txt", "w")
        if not path.exists(self.path + "points.txt"):
            open(self.path + "points.txt", "w")

    def get_blacklist(self) -> List:
        """
        Return blacklisted msgids.

        Return:
            List: List of blacklisted msgids.
        """
        return list(filter(lambda x: len(x) > 0,
                           open("blacklist.txt").read().split("\n")))

    def get_counts(self, echoareas: List) -> Dict:
        """
        Counts the number of messages in a echoarea.

        Args:
            echoareas (List): Echoareas names.

        Return:
            Dict: Dict of echoareas counts (str) {"name": int}.
        """
        counts = {}
        for echoarea in echoareas:
            if not path.exists(self.path + "echo/" + echoarea):
                counts[echoarea] = 0
            else:
                counts[echoarea] = len(open(self.path + "echo/" + echoarea).read().split()) - 1
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
        for echoarea in echoareas:
            if path.exists(self.path + "echo/" + echoarea):
                with open(echoarea) as f:
                    for msgid in f.read().split():
                        if len(msgid) > 0:
                            index.append(msgid)
        return index

    def is_message_exists(self, msgid: str) -> bool:
        """
        Check message exists in echoarea.

        Args:
            msgid (str): Msgid of message.

        Return:
             bool: True if message exists.
        """
        if path.exists("msg/" + msgid):
            return True
        return False

    def get_message(self, msgid: str) -> str:
        """
        Get message by msgid.

        Args:
            msgid (str): Msgid.

        Return:
            str: Message as plain text.
        """
        try:
            return open(self.path + "msg/" + msgid).read()
        except FileNotFoundError:
            raise

    def save_message(self, echoarea: str, msgid: str, message: str, other: object = None) -> bool:
        """
        Save message to base.

        Args:
            echoarea (str): Echoarea name.
            msgid (str): Msgid.
            message (str): Message as plain text.
            other (object): Additional argument.

        Return:
            bool: Save status. True if message saved else False.
        """
        if not self.is_message_exists(msgid):
            open(self.path + "echo/" + echoarea, "a").write(msgid + "\n")
            open(self.path + "msg/" + msgid, "w").write(message)
            return True
        return False

    def save_messages(self, bundle: List) -> int:
        """
        Save messages of bundle to base.

        Args:
            bundle (List): Bundle as List of dict:
                           {"msgid", "encoded"}.

        Return:
            int: Saved messages count.
        """
        saved_counter = 0
        for message in bundle:
            body = urlsafe_b64decode(message["encoded"]).decode("utf-8")
            echoarea = body.split("\n")[1]
            if self.save_message(echoarea, message["msgid"], body):
                saved_counter += 1
        return saved_counter

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
        points = open("points.txt").read().split("\n")
        exists = False
        for point in points:
            if username == point.split(":")[0]:
                exists = True
        if not exists:
            authstr = Base.generate_authstr(username)
            open("points.txt", "a").write("{}:{}\n".format(username, authstr))
            return authstr
        return ""

    def check_point(self, nodename: str, authstr: str) -> Dict:
        """
        Check for a point.

        Args:
            authstr (str): Search authstr.

        Return:
            Dict: Point informationa:
                  {"name", "address"} or None.
        """
        points = open("points.txt").read().split("\n")
        i = 0
        for point in points:
            i += 1
            fields = point.split(":")
            if authstr == fields[1]:
                return {"name": point[0], "addr": "{},{}".format(nodename, i)}
        return None

    def point_list(self) -> List:
        points = open("points.txt").read().split("\n")
        return list([x.split(":") for x in points if len(x) > 0])
