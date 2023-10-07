import os
from dataclasses import dataclass

import dataclass_factory
import yaml
from yaml.loader import SafeLoader

from db_api.postgresql import Database

db = Database()


def load_yaml():
    with open(os.path.join(os.getcwd(), "config.yaml"), 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=SafeLoader)


def dump_yaml(data):
    with open(os.path.join(os.getcwd(), "config.yaml"), 'w', encoding='utf-8') as f:
        print(data)
        yaml.dump(data, f, allow_unicode=True)

@dataclass
class Config:
    token: str
    channel: str
    link: str
    link_help_game: str
    yookassa_api: str
    yookassa_id: str
    premium: int
    priz: int
    link_get_priz: str
    admins_list: list
    info: str
    DOMEN: str
    dsn: str
    utm: dict
    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        if setup:
            print("изменен атрибут ", key)
            dump_yaml(config.__dict__)


setup = False
factory = dataclass_factory.Factory()
config: Config = factory.load(load_yaml(), Config)
setup = True
