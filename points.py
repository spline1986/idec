from base.sqlite import Sqlite
import json
import sys


def usage():
    print("Usage:", args[0], "-h|-list|-add")
    sys.exit(0)


config = json.loads(open("server.json").read())
base = Sqlite(config["base"])
args = sys.argv
if len(args) == 1 or args[1] == "-h":
    usage()
elif args[1] == "-list":
    print("\n".join(base.point_list()))
elif args[1] == "-add":
    authstr = base.add_point(args[2])
    print("Username: {}\nAuthstr: {}\n".format(
        args[2], authstr
    ))
else:
    usage()
