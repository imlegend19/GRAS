import configparser


class Config:
    def __init__(self):
        self.config = configparser.RawConfigParser()

    def _create_config(self, name, arg_groups):
        groups = {k: v for k, v in arg_groups.items() if k not in ['positional arguments', 'optional arguments']}
        for group in groups:
            self.config.add_section(group)
            group_dict = vars(groups[group])
            for key in group_dict:
                self.config.set(group, key, group_dict[key])
        DEFAULT_START_DATE = self.config.get('MINER-SETTINGS', 'start_date')
        DEFAULT_END_DATE = self.config.get('MINER-SETTINGS', 'end_date')
        self.config.add_section('REPOSITORY-LIST')
        self.config.set('REPOSITORY-LIST', 'owner/name', 'start_date, end_date')
        self.config.set('REPOSITORY-LIST', 'sympy/sympy', f'{DEFAULT_START_DATE}, {DEFAULT_END_DATE}')
        self.config.set('REPOSITORY-LIST', 'flutter/flutter', '')
        with open(f'{name}.ini', 'w') as cfgfile:
            self.config.write(cfgfile)
