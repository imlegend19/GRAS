class VariableModel:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind


class FunctionModel:
    def __init__(self, name, params):
        self.name = name
        self.params = params
