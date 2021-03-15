"""
Object implementation of IDEC-protocol client.

Copyright (c) 2021, Andrew Lobanov.
License: GNU GPL 3 (see LICENSE for details).
"""

from base64 import b64encode
from requests import get, post
from requests.models import Response
from typing import Dict, List, Set


class Uplink:
    """
    This object contains URL and authstr of IDEC-node.

    Args:
        url (str): Uplink URL.
        auth (str, optional): Point authstr.
    """
    def __init__(self, url: str, auth: str = None):
        if url.endswith("/"):
            self.url = url
        else:
            self.url = url + "/"
        self.auth = auth
            
    def get_list_txt(self) -> List:
        """
        Downloads a list of echoareas from the uplink.

        Return:
            list(dict): List of dicts(str, int, str)
                        {"name", "count", "description"}.
        """
        response = get(self.url + "list.txt")
        echoareas = []
        for line in response.text.split("\n"):
            if len(line) > 0:
                splitted = line.split(":")
                echoareas.append({
                    "name": splitted[0],
                    "count": int(splitted[1]),
                    "description": ":".join(splitted[2:])
                })
        return echoareas

    def get_blacklist(self) -> Set:
        """
        Downloads a blacklist of messages from the uplink.

        Return:
            set(str): Set of msgids.
        """
        response = get(self.url + "blacklist.txt")
        msgids = set()
        for line in response.text.split("\n"):
            if len(line) > 0:
                msgids.add(line)
        return msgids

    def get_echoarea(self, echoarea: str) -> List:
        """
        Downloads echoarea index from uplink (e/ scheme).

        Args:
            echoarea(str): Echoarea name.

        Return:
            list(str): List of msgids.
        """
        response = get("{}/e/{}".format(self.url, echoarea))
        msgids = []
        for line in response.text.split("\n"):
            if len(line) > 0:
                msgids.append(line)
        return msgids

    def get_index(self, echoareas: List, depth: int = 0) -> List:
        """
        Downloads echoareas index from uplink (u/e/ scheme).

        Args:
            echoareas(list[str]): List of echoareas names.
            depth(int, optional): Count of msgids from the end of the
                                  uplink index.

        Return:
            list(str): List of msgids.
        """
        url = "{}u/e/{}".format(self.url, "/".join(echoareas))
        if depth > 0:
            url += "/-{0}:{0}".format(depth)
        response = get(url)
        msgids = []
        for line in response.text.split("\n"):
            if len(line) > 0 and "." not in line:
                msgids.append(line)
        return msgids

    def get_message(self, msgid: str) -> str:
        """
        Downloads message from uplink (m/ scheme).

        Args:
            msgid(str): Msgid.

        Return
            str: Raw text message.
        """
        response = get("{}/m/{}".format(self.url, msgid))
        return response.text

    @staticmethod
    def split(items: List, size: int = 40) -> List:
        """
        Splits list by size.

        Args:
            items(list): Split list.
            size(int, default 40): Slice size.

        Return:
            generator: Splitted list.
        """
        for i in range(0, len(items), size):
            yield items[i:i + size]

    def get_bundle(self, msgids: List) -> List:
        """
        Downloads message bundle from uplink.

        Args:
            msgids(List): List of msgids.

        Return:
            list(dict): List of dicts (str, str) {"msgid", "encoded"},
                        where "encoded" contains encoded message.
        """
        blocks = self.split(msgids)
        bundle = []
        for block in blocks:
            response = get("{}/u/m/{}".format(self.url, "/".join(block)))
            for line in response.text.split("\n"):
                if len(line) > 0:
                    bundled = line.split(":")
                    bundle.append({"msgid": bundled[0], "encoded": bundled[1]})
        return bundle

    def send_message(self, message: str) -> str:
        """
        Sends message to uplink.

        Args:
            message(str): Points message.

        Return:
            str: Uplink response string.

        Points message format:
            <ECHOAREA>
            <TO>
            <SUBJECT>

            [@repto:<MSGID>]
            <TEXT>
        """
        data = {
            "pauth": self.auth,
            "tmsg": b64encode(message.encode()),
        }
        response = post(self.url + "u/point", data=data)
        return response.text

    def get_counts(self, echoareas: List) -> Dict:
        """
        Downloads echoareas counts from upllink.

        Args:
            echoareas(list): Echoareas names list.

        Return:
            dict: Dict of echoareas counts (str) {"name"}.
        """
        response = get("{}/x/c/{}".format(self.url, "/".join(echoareas)))
        counts = {}
        for line in response.text.split("\n"):
            if len(line) > 0:
                count = line.split(":")
                counts[count[0]] = int(count[1])
        return counts

    def get_filelist(self):
        """
        Downloads files list available for file request.

        Return:
            list(dict): List of dicts (str, int, str)
                        {"name", "size", "description"}.
        """
        if self.auth:
            data = {"pauth": self.auth}
            response = post(self.url + "/x/filelist", data=data)
        else:
            response = get(self.url + "/x/filelist")
        filelist = []
        for line in response.text.split("\n"):
            if len(line) > 0:
                fields = line.split(":")
                filelist.append({
                    "name": fields[0],
                    "size": int(fields[1]),
                    "description": fields[2],
                })
        return filelist

    @staticmethod
    def save_file(destination: str, filename: str, response: Response):
        response.raw.decode_content = True
        path = destination
        if not path.endswith("/"):
            path += "/"
        with open(path + filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

    def download_file(self, destination: str, filename: str):
        """
        Downloads a file using file request and save it at destination.

        Args:
            filename (str): Filename.
            destination (str): The path of the saved file.
        """
        data = {
            "pauth": self.auth,
            "filename": filename
        }
        response = post(self.url + "x/file", data=data, stream=True)
        self.save_file(destination, filename, response)

    def get_f_list_txt(self) -> List:
        """
        Downloads a list of fileechoareas from the uplink.

        Return:
            list(dict): List of dicts(str, int, str)
                        {"name", "count", "description"}.
        """
        response = get(self.url + "f/list.txt")
        fechoareas = []
        for line in response.text.split("\n"):
            if len(line) > 0:
                fechoarea = line.split(":")
                fechoareas.append({
                    "name": fechoarea[0],
                    "count": fechoarea[1],
                    "description": fechoarea[2]
                })
        return fechoareas

    def get_f_blacklist_txt(self) -> Set:
        """
        Downloads a blacklist of messages from the uplink.

        Return:
            set(str): Set of fids.
        """
        response = get(self.url + "f/blacklist.txt")
        fids = set()
        for line in response.text.split("\n"):
            if len(line) > 0:
                fids.add(line)
        return fids

    def get_fileechoareas_count(self, echoareas: List) -> Dict:
        """
        Downloads fileechoareas counts from upllink.

        Args:
            echoareas(list): Echoareas names list.

        Return:
            dict: Dict of echoareas counts (str) {"name"}.
        """
        response = get("{}f/c/{}".format(self.url, "/".join(echoareas)))
        counts = {}
        for line in response.text.split("\n"):
            if len(line) > 0:
                fechoarea = line.split(":")
                counts[fechoarea[0]] = int(fechoarea[1])
        return counts

    def get_fileechoareas_filelist(self, fileechoes: List) -> List:
        """
        Downloads fileechoareas filelist.

        Args:
            fileechoareas list(str): List of fileechoareas names.

        Return:
            list(str): List of raw lines of feileechoareas index in format:
                       fid:filename:size:address:description.
        """
        response = get("{}f/e/{}".format(self.url, "/".join(fileechoes)))
        files = []
        for line in response.text.split("\n"):
            if len(line) > 0 and ":" in line:
                files.append(line)
        return files

    def download_fileechoarea_file(self, fecho: str, fid_name: str, destination: str):
        """
        Downloads a file from fileechoarea and save it at destination.

        Args:
            fecho (str): Fileechoarea name.
            fid_name (str): Fid and filename in format "fid:filename".
                           Can be a full line of fileechoarea index.
            destination (str): The path of the saved file.
        """
        frow = fid_name.split(":")
        response = get("{}f/f/{}/{}".format(self.url, fecho, frow[0]), stream=True)
        self.save_file(destination, frow[1], response)

    def send_file_to_fileechoarea(self, fecho: str, filename: str, description: str) -> str:
        """
        Sends file to fileechoarea.

        Args:
            fecho (str): Fileechoarea name.
            filename (str): Filename of sending file.
            description(str): Short description of the file (< 1kb).

        Return:
            str: Uplink response string.
        """
        data = {
            "pauth": self.auth,
            "fecho": fecho,
            "dsc": description
        }
        files = {
            "file": open(filename, "rb")
        }
        response = post(self.url + "f/p", data=data, files=files)
        return response.text

    def push(self, auth: str, bundle: str, echoarea: str) -> str:
        """
        Push bundle to uplink (u/push).

        Args:
            auth (str): Pusher authstr.
            bundle (str): Bundle. "msgid:base64" format.
            echoarea (str): Echoarea name.

        Return:
            str: Uplink response string.
        """
        data = {
            "nauth": auth,
            "upush": bundle,
            "echoarea": echoarea
        }
        response = post(self.url + "u/push", data=data)
        return response.text
