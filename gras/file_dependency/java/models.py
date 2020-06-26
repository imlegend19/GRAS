from gras.base_model import BaseModel


class ImportModel(BaseModel):
    def __init__(self, pkg, name, lineno):
        super().__init__()

        self.package = pkg
        self.name = name
        self.lineno = lineno

    def object_decoder(self, **kwargs):
        ...


class TypeParameterModel(BaseModel):
    def __init__(self, annotations, name, extends, lineno):
        super().__init__()

        self.annotations = annotations
        self.name = name
        self.extends = extends
        self.lineno = lineno

    def object_decoder(self, **kwargs):
        ...


class CallModel(BaseModel):
    def __init__(self, reference, target):
        super().__init__()

        self.reference = reference
        self.target = target

    def object_decoder(self, **kwargs):
        ...
