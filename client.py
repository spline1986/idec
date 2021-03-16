from base import Base
from typing import List
from uplink import Uplink


class Client:
    def __init__(self, uplink: Uplink, base: Base, echoareas: List = None):
        self.uplink = uplink
        self.base = base
        self.echoareas = echoareas

    def add_echoarea(self, echoarea: str):
        if echoarea not in self.echoareas:
            self.echoareas.append(echoarea)

    def delete_echoarea(self, echoarea: str):
        self.echoareas.remove(echoarea)

    def add_echoareas(self, echoareas: List):
        self.echoareas = self.echoareas + echoareas

    def delete_echoareas(self, echoareas: List):
        for echoarea in echoareas:
            self.echoareas.remove(echoarea)

    @property
    def index_offset(self):
        remote_counts = self.uplink.get_counts(self.echoareas)
        local_counts = self.base.get_counts(self.echoareas)
        maximum = 0
        for key in local_counts.keys():
            if remote_counts[key] > local_counts[key]:
                current = remote_counts[key] - local_counts[key]
                if current > maximum:
                    maximum = current
        return maximum

    def download_mail(self) -> int:
        depth = self.index_offset
        if depth > 0:
            index = self.uplink.get_index(self.echoareas, depth)
            bundle = self.uplink.get_bundle(index)
            return self.base.save_messages(bundle)
        return 0

    def send_message(self, message: str):
        self.uplink.send_message(message)