import json
import sys
from idec.client import Client
from base.sqlite import Sqlite
from typing import Dict, List, Union
from idec.uplink import Uplink


def load_config(filename: str = "fetcher.json") -> Dict[str,
                                                        Union[str, List[str]]]:
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
