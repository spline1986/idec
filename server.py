from base64 import urlsafe_b64encode
from bottle import post, request, response, route, run
from sqlite import Sqlite
import json


@route("/")
def index():
    response.set_header("Content-Type", "text/plain; charset=utf-8")
    return "Welcome to IDEC!"


@route("/e/<echoarea>")
def echoarea_index(echoarea):
    response.set_header("Content-Type", "text/plain; charset=utf-8")
    return "\n".join(base.get_index([echoarea])) + "\n\n"


@route("/m/<msgid>")
def message(msgid):
    response.set_header("Content-Type", "text/plain; charset=utf-8")
    return base.get_message(msgid)


@route("/u/e/<echoareas:path>")
def universal_echoareas_index(echoareas):
    response.set_header("Content-Type", "text/plain; charset=utf-8")
    echoareas = echoareas.split("/")
    start, end, slc = 0, 0, False
    if ":" in echoareas[-1]:
        slc = echoareas[-1].split(":")
        start, end, slc = int(slc[0]), int(slc[1]), True
        echoareas = echoareas[:-1]
    ue_index = []
    for echoarea in echoareas:
        ue_index.append(echoarea)
        ss = start
        index = base.get_index([echoarea])
        if start < 0 and start + len(index) < 0:
            ss = 0
        elif start > len(index):
            ss = end * -1
        if start + end == 0:
            ue_index = ue_index + index[ss:]
        elif slc:
            ue_index = ue_index + index[ss:ss + end]
        else:
            ue_index = ue_index + index
    return "\n".join(ue_index) + "\n\n"


@route("/u/m/<msgids:path>")
def universal_bundle(msgids):
    response.set_header("Content-Type", "text/plain; charset=utf-8")
    bundle = []
    for msgid in msgids.split("/"):
        if base.is_message_exists(msgid):
            encoded = urlsafe_b64encode(base.get_message(msgid).encode())
            bundle.append(msgid + ":" + encoded.decode("utf-8"))
    return "\n".join(bundle) + "\n\n"


@post("/u/point")
@route("/u/point/<pauth>/<tmsg>")
def receive_message(pauth: str, tmsg: str):
    response.set_header("Content-Type", "text/plain; charset=utf-8")
    if request.method == "POST":
        pauth = request.POST["pauth"]
        tmsg = request.POST["tmsg"]
    point = base.check_point(pauth)
    status = base.toss_message(point, tmsg)
    return status


config = json.loads(open("server.json").read())
base = Sqlite(config["base"])
run(host="0.0.0.0", port=62220)
