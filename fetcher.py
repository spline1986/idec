import json
from client import Client
from sqlite import Sqlite
from uplink import Uplink

config = json.loads(open("fetcher.json").read())
base = Sqlite(config["base"])
uplink = Uplink(config["uplink"])
client = Client(uplink, base, config["echoareas"])
print(client.download_mail(), "messages downloaded.")
