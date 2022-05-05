from dataclasses import dataclass

from typing import Dict


@dataclass
class Registry:
    temperature: float = 1.0
    length: int = 100


class Storage:

    def __init__(self):
        self.data: Dict[int, Registry] = {-1: Registry()}

    def checkout(self, user_id: int):
        if user_id not in self.data.keys():
            self.data.update({user_id: Registry()})

    def get_temperature(self, user_id: int):
        return self.data[user_id].temperature

    def set_temperature(self, user_id: int, temperature: float):
        self.data[user_id].temperature = temperature

    def get_length(self, user_id: int):
        return self.data[user_id].length

    def set_length(self, user_id: int, length: int):
        self.data[user_id].length = length
