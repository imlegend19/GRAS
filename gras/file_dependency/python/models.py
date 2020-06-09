from gras.base_model import BaseModel


class DirectoryModel(BaseModel):
    def __init__(self, name, files, directories, total_loc, total_files, total_classes, total_functions,
                 total_global_variables):
        super().__init__()

        self.name = name
        self.files = files
        self.directories = directories
        self.total_loc = total_loc
        self.total_files = total_files
        self.total_classes = total_classes
        self.total_functions = total_functions
        self.total_global_variables = total_global_variables

    def object_decoder(self, **kwargs):
        ...


class FileModel(BaseModel):
    def __init__(self, name, loc, classes, functions, variables, imports):
        super().__init__()

        self.name = name
        self.loc = loc
        self.classes = classes
        self.functions = functions
        self.variables = variables
        self.imports = imports
        self.import_list = [import_.module for import_ in imports]
        self.total_classes = len(self.classes)
        self.total_functions = len(self.functions)
        self.total_variables = len(self.variables)
        self.total_imports = len(self.imports)

    def object_decoder(self, **kwargs):
        ...


class DefModel(BaseModel):
    def __init__(self, subtype, name, decorators, arguments, functions, classes, imports, variables, docstring, line):
        super().__init__()

        self.subtype = subtype
        self.name = name
        self.decorators = decorators
        self.arguments = arguments
        self.functions = functions
        self.classes = classes
        self.imports = imports
        self.variables = variables
        self.docstring = docstring
        self.line = line
        self.total_classes = len(self.classes)
        self.total_functions = len(self.functions)
        self.total_variables = len(self.variables)
        self.total_imports = len(self.imports)
        self.total_decorators = len(self.decorators)

    def object_decoder(self, **kwargs):
        ...


class ImportModel(BaseModel):
    def __init__(self, name, as_name, line, module=None):
        super().__init__()

        self.module = module
        self.name = name
        self.as_name = as_name
        self.line = line

    def object_decoder(self, **kwargs):
        ...


class DecoratorModel(BaseModel):
    def __init__(self, subtype, name, value, line, total_args=None, total_kwargs=None):
        super().__init__()

        self.subtype = subtype
        self.name = name
        self.value = value
        self.line = line
        self.total_args = total_args
        self.total_kwargs = total_kwargs

    def object_decoder(self, **kwargs):
        ...


class ArgModel(BaseModel):
    def __init__(self, subtype, name, value):
        super().__init__()

        self.subtype = subtype
        self.name = name
        self.value = value

    def object_decoder(self, **kwargs):
        ...


class KwargModel(BaseModel):
    def __init__(self, subtype, name, value):
        super().__init__()

        self.subtype = subtype
        self.name = name
        self.value = value

    def object_decoder(self, **kwargs):
        ...


class VariableModel(BaseModel):
    def __init__(self, scope, subtype, name, line):
        super().__init__()

        self.scope = scope
        self.subtype = subtype
        self.name = name
        self.line = line

    def object_decoder(self, **kwargs):
        ...
