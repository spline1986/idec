import json
import sys
from client import Client
from sqlite import Sqlite
from typing import Dict
from uplink import Uplink


def load_config(filename: str = "fetcher.json") -> Dict:
    return json.loads(open(filename).read())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config = load_config(sys.argv[1])
    else:
        config = load_config()
    base = Sqlite(config["base"])
    uplink = Uplink(config["uplink"])
    client = Client(uplink, base, config["echoareas"])
    print(client.download_mail(), "messages downloaded.")
