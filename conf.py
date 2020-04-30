import json
config_file = open("config.json", "r")
config = json.load(config_file)
config_file.close()


def get_item(key,item):
    data = config[key][item]
    if data:
        return data
    else:
        raise KeyError(f"'{item}' is empty")
        
def set_item(key,item,obj):
    config[key][item] = obj
    with open("config.json","w") as write_config:
        json.dump(config, write_config)

def reset():
    data = {"auth":{},"repo": {}}
    with open("config.json","w") as write_config:
        json.dump(data, write_config)

    
        
        
