import configparser

class Config:

    def __init__(self):
        self.config = configparser.RawConfigParser()    
        with open('config.ini', 'w') as cfgfile:
            self.config.write(cfgfile)

    def set_section(self, section):
        self.config.add_section(section)

    def set(self, section, option, value):
        self.config.read('config.ini')
        if self.config.has_section(section) == False:
            self.config.add_section(section)
        
        self.config.set(section,option,value)
        with open('config.ini', 'w') as cfgfile:
            self.config.write(cfgfile)

    def get(self, section, option):
        self.config.read('config.ini')
        return self.config.get('default', 'option1')


conf = Config()
conf.set('default', 'option1', 'value1')
conf.set('default', 'option2', 'value2')
print(conf.get('default','option'))