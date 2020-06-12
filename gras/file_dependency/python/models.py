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
    def __init__(self, name, path, loc, classes, functions, variables, imports):
        super().__init__()

        self.name = name
        self.path = path
        self.loc = loc
        self.classes = classes
        self.functions = functions
        self.variables = variables
        self.imports = imports

    @property
    def total_classes(self):
        return len(self.classes)

    @property
    def total_functions(self):
        return len(self.functions)

    @property
    def total_variables(self):
        return len(self.variables)

    @property
    def total_imports(self):
        return len(self.imports)

    @property
    def import_list(self):
        return [import_.name for import_ in self.imports] if self.imports else None

    def object_decoder(self, **kwargs):
        ...


class DefModel(BaseModel):
    def __init__(self, subtype, name, decorators, arguments, functions, classes, imports, variables, docstring, lineno):
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
        self.lineno = lineno

    @property
    def argument_list(self):
        return [argument.name for argument in self.arguments] if self.arguments else None

    @property
    def decorator_list(self):
        return [decorator.name for decorator in self.decorators] if self.decorators else None

    def object_decoder(self, **kwargs):
        ...


class ImportModel(BaseModel):
    def __init__(self, name, as_name, lineno, module=None):
        super().__init__()

        self.module = module
        self.name = name
        self.as_name = as_name
        self.lineno = lineno

    def object_decoder(self, **kwargs):
        ...


class DecoratorModel(BaseModel):
    def __init__(self, name, value, lineno):
        super().__init__()

        self.name = name
        self.value = value
        self.lineno = lineno

    def object_decoder(self, **kwargs):
        ...


class ArgModel(BaseModel):
    def __init__(self, subtype, name, value, lineno, annotation):
        super().__init__()

        self.subtype = subtype
        self.name = name
        self.value = value
        self.lineno = lineno
        self.annotation = annotation

    def object_decoder(self, **kwargs):
        ...


class AttributeModel(BaseModel):
    def __init__(self, name, lineno, value):
        super().__init__()

        self.name = name
        self.lineno = lineno
        self.value = value

    def object_decoder(self, **kwargs):
        ...


class CallModel(BaseModel):
    def __init__(self, lineno, func):
        super().__init__()

        self.lineno = lineno
        self.func = func

    def object_decoder(self, **kwargs):
        ...


class VariableModel(BaseModel):
    def __init__(self, subtype, name):
        super().__init__()

        self.subtype = subtype
        self.name = name

    def object_decoder(self, **kwargs):
        ...
