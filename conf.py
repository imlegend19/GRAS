import json
import requests

config_file = open("config.json", "r")
config = json.load(config_file)
config_file.close()


def get_item(key, item):
    data = config[key][item]
    if data:
        return data
    else:
        raise KeyError(f"'{item}' is empty")


def set_item(key, item, obj):
    config[key][item] = obj
    with open("config.json", "w") as write_config:
        json.dump(config, write_config)


def reset():
    data = {"AUTH": {}, "repo": {}}
    with open("config.json", "w") as write_config:
        json.dump(data, write_config)


#TODO
def auth_key_validator(auth_key):
    return True


def repo_validator(repo):
    res = requests.get("https://api.github.com/repos/{}".format(repo)).ok
    return res


def user_validator(user):
    res = requests.get("https://api.github.com/users/{}".format(user)).ok
    return res


#TODO
def pass_validator(user, password):
    return True