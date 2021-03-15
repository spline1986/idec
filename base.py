"""
Message base abstract class.
"""

from base64 import urlsafe_b64encode, urlsafe_b64decode
from hashlib import sha256
from time import time
from typing import Callable, Dict, List
from sys import getsizeof


class Base:
    def __init__(self, path: str):
        pass

    def check_base(self):
        """
        Checks base and create this if not exists.
        """
        pass

    def get_counts(self, echoareas: List) -> Dict:
        """
        Counts the number of messages in a echoarea.

        Args:
            echoarea (List): Echoareas names.

        Return:
            Dict: Dict of echoareas counts (str) {"name": int}.
        """
        pass

    def get_index(self, echoareas: List) -> List:
        """
        Get msgids of echoareas and return they.

        Args:
            echoareas (List): Echoareas names.

        Return:
            List: Msgids.
        """
        pass

    def is_message_exists(self, echoarea: str, msgid: str) -> bool:
        """
        Check message exists in echoarea.

        Args:
            echoarea (str): Echoarea name.
            msgid (str): Msgid of message.

        Return:
             bool: True if message exists.
        """
        ...

    def get_message(self, msgid: str) -> str:
        """
        Get message by msgid.

        Args:
            msgid (str): Msgid.

        Return:
            str: Message as plain text.
        """
        pass

    def save_message(self, echoarea: str, msgid: str, message: str, other: object = None):
        """
        Save message to base.

        Args:
            echoarea (str): Echoarea name.
            msgid (str): Msgid.
            message (str): Message as plain text.
            other (object): Additional argument.
        """
        pass
        
    def save_messages(self, bundle: List):
        """
        Save messages of bundle to base.

        Args:
            bundle (List): Bundle as List of dict:
                           {"msgid", "encoded"}.
        """
        pass

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
        pass

    @staticmethod
    def build_hash(message: str) -> str:
        """
        Build msgid by message.

        Args:
            message (str): Message as plain text.

        Return:
            str: Msgid.
        """
        hsh = urlsafe_b64encode(sha256(message.encode()).digest())
        return hsh.decode("utf-8")[:20].replace("-", "A").replace("_", "z")

    @staticmethod
    def parse_point_message(encoded: str) -> Dict:
        """
        Decode and parse point's message.

        Args:
            encoded (str): uelsafe base64 encoded point's message.

        Return:
             Dict: Parsed message as Dict:
                   { "tags", "echoarea", "msgto", "subject", "body" }.
        """
        message = urlsafe_b64decode(encoded).decode("utf-8").split("\n")
        if message[4].startswith("@repto:"):
            repto = message[4].replace("@repto:", "")
            body = "\n".join(message[5:])
        else:
            repto = None
            body = "\n".join(message[4:])
        tags = "ii/ok"
        if repto:
            tags = tags + "/repto/" + repto
        return {
            "tags": tags,
            "echoarea": message[0],
            "msgto": message[1],
            "subject": message[2],
            "body": body
        }

    @staticmethod
    def build_message(point: Dict, encoded: str) -> (str, str):
        """
        Build message by point information and pont's message.

        Args:
            point (dics): Point information {"name", "address"}.
            encoded (str): Base64 encoded point's message.

        Return:
            str: Echoarea name.
            str: Ready message.
        """
        parsed_message = Base.parse_point_message(encoded)
        date = str(int(time()))
        msg = "{}\n".format(parsed_message["tags"])
        msg = msg + "{}\n".format(parsed_message["echoarea"])
        msg = msg + "{}\n".format(date)
        msg = msg + "{}\n".format(parsed_message["echoarea"])
        msg = msg + "{}\n".format(point["name"])
        msg = msg + "{}\n".format(point["address"])
        msg = msg + "{}\n".format(parsed_message["msgto"])
        msg = msg + "{}\n\n".format(parsed_message["subject"])
        msg = msg + "{}\n".format(parsed_message["body"])
        return parsed_message["echoarea"], msg

    @staticmethod
    def toss_message(self, save_message: Callable, point: Dict, encoded: str) -> str:
        """
        Build message, make msgid and save it.

        Args:
            save_message (Callable): Save message function.
            point (Dict): Point information {"name", "address"}.
            encoded (str): Base64 encoded point's message.

        Return:
            str: Response text.
        """
        echoarea, message = Base.build_message(point, encoded)
        if getsizeof(message) <= 65535:
            h = Base.build_hash(message)
            save_message(echoarea, h, message)
            return "msg ok:" + h
        else:
            return "error: msg big!"
