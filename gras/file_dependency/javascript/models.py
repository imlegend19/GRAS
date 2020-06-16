from gras.base_model import BaseModel


class ImportModel(BaseModel):
    def __init__(self, name, asname, line, module=None):
        super().__init__()

        self.name = name
        self.asname = asname
        self.module = module
        self.line = line

    def object_decoder(self, **kwargs):
        ...