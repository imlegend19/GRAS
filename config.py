import configparser


class Config:
    def __init__(self):
        self.config = configparser.RawConfigParser()
        # with open('config.ini', 'w') as cfgfile:
        #     self.config.write(cfgfile)

    #
    # def set_section(self, section):
    #     self.config.add_section(section)
    #
    # def _set(self, section, option, value):
    #     self.config.read('config.ini')
    #     if not self.config.has_section(section):
    #         self.config.add_section(section)
    #
    #     self.config.set(section, option, value)
    #     with open('config.ini', 'w') as cfgfile:
    #         self.config.write(cfgfile)
    #
    # def _get(self, section, option):
    #     self.config.read('config.ini')
    #     try:
    #         return self.config.get(section, option)
    #     except configparser.NoSectionError:
    #         print(f"{section} is not present in the config file")
    #     except configparser.NoOptionError:
    #         print(f"{option} is not present in the {section} section")

    def _create_config(self, name, arg_groups):
        groups = {k: v for k, v in arg_groups.items() if k not in ['positional arguments', 'optional arguments']}
        for group in groups:
            self.config.add_section(group)
            group_dict = vars(groups[group])
            for key in group_dict:
                self.config.set(group, key, group_dict[key])
        self.config.add_section('REPOSITORY-LIST')
        self.config.set('REPOSITORY-LIST', 'owner/name', 'start_date, end_date')
        self.config.set('REPOSITORY-LIST', 'sympy/sympy', ' $DEFAULT_START_DATE, $DEFAULT_END_DATE')
        self.config.set('REPOSITORY-LIST', 'flutter/flutter', '')
        with open(f'{name}.ini', 'w') as cfgfile:
            self.config.write(cfgfile)
