from base import Base
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
        if not path.exists(self.path + "msg"):
            mkdir(self.path + "msg")
        if not path.exists(self.path + "echo"):
            mkdir(self.path + "echo")
        if not path.exists(self.path + "blacklist.txt"):
            open(self.path + "blacklist.txt", "w")

    def get_counts(self, echoareas: List) -> Dict:
        counts = {}
        for echoarea in echoareas:
            if not path.exists(self.path + "echo/" + echoarea):
                counts[echoarea] = 0
            counts[echoarea] = len(open(self.path + "echo/" + echoarea).read().split()) - 1
        return counts

    def get_index(self, echoareas: List) -> List:
        index = []
        for echoarea in echoareas:
            if path.exists(self.path + "echo/" + echoarea):
                with open(echoarea) as f:
                    for msgid in f.read().split():
                        if len(msgid) > 0:
                            index.append(msgid)
        return index

    def is_message_exists(self, echoarea: str, msgid: str) -> bool:
        if not path.exists(self.path + "echo/" + echoarea):
            return False
        index = open(self.path + "echo/" + echoarea).read().split("\n")
        if msgid in index:
            return True
        return False

    def get_message(self, msgid: str) -> str:
        try:
            return open(self.path + "msg/" + msgid).read()
        except FileNotFoundError:
            raise

    def save_message(self, echoarea: str, msgid: str, message: str, other: object = None) -> bool:
        if not self.is_message_exists(echoarea, msgid):
            open(self.path + "echo/" + echoarea, "a").write(msgid + "\n")
            open(self.path + "msg/" + msgid, "w").write(message)
            return True
        return False

    def save_messages(self, bundle: List) -> int:
        saved_counter = 0
        for message in bundle:
            body = urlsafe_b64decode(message["encoded"]).decode("utf-8")
            echoarea = body.split("\n")[1]
            if self.save_message(echoarea, message["msgid"], body):
                saved_counter += 1
        return saved_counter

    def toss_message(self, point: Dict, encoded: str) -> str:
        return super().toss_message(self.save_message, point, encoded)
