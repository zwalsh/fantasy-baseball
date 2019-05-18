import os
from pathlib import Path

from notifications.client.dev import DevClient
from notifications.client.pushed import PushedClient
from notifications.notifier import Notifier


def current_notifier(user):
    env = os.getenv('ENV', 'DEV')
    if env == 'PROD':
        return prod_notifier(user)
    else:
        return Notifier(DevClient())


def prod_notifier(user):
    return Notifier(PushedClient(user, user_pushed_id(user), app_key(), app_secret()))


def app_key():
    return read_text("config/pushed_config/app_key.txt")


def app_secret():
    return read_text("config/pushed_config/app_secret.txt")


def user_pushed_id(user):
    return read_text("config/pushed_config/{}_pushed_id.txt".format(user))


def read_text(rel_path_str):
    abs_path = Path.cwd() / rel_path_str
    return abs_path.read_text()
