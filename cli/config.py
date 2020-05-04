import os
import configparser
configfile_name = "config.ini"
config = configparser.ConfigParser()


# Check if there is already a configurtion file
def create_config():
    if not os.path.isfile(configfile_name):
        # Create the configuration file as it doesn't exist yet
        cfgfile = open(configfile_name, "w")

        # Add content to the file
        Config = configparser.RawConfigParser()
        Config.add_section("AUTH")
        Config.add_section("repo")
        Config.write(cfgfile)
        cfgfile.close()
    else:
        print("it exists")


def get_item(section, key):
    config.read(configfile_name)
    item = config[section][key]
    return item


def set_item(section, key, value):
    config.read(configfile_name)
    config[section][key] = value
    with open(configfile_name, 'w') as configfile:
        config.write(configfile)


def check(section, key):
    config.read(configfile_name)
    return key in config[section]


#config.read(configfile_name)
#set_item('AUTH', 'user_name', '1233')
# print(get_item('AUTH', 'AUTH_KEY'))
# print(check('AUTH','AUTH_KEY'))
#print(config.sections())
#create_config()