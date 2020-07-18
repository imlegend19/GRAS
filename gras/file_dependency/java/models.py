from gras.base_model import BaseModel


class JarModel(BaseModel):
    def __init__(self, name, files):
        super().__init__()

        self.name = name
        self.files = files

    def object_decoder(self, **kwargs):
        ...


class FileModel(BaseModel):
    def __init__(self, name, pkg, imports, classes, interfaces, enums, annotations, loc):
        super().__init__()

        self.name = name
        self.pkg = pkg
        self.imports = imports
        self.classes = classes
        self.interfaces = interfaces
        self.enums = enums
        self.annotations = annotations
        self.loc = loc

    def object_decoder(self, **kwargs):
        ...


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
    def __init__(self, reference, target, lineno):
        super().__init__()

        self.reference = reference
        self.target = target
        self.lineno = lineno

    def object_decoder(self, **kwargs):
        ...


class MethodModel(BaseModel):
    def __init__(self, name, return_type, total_args, throws, calls, loc, modifiers=None):
        super().__init__()

        self.name = name
        self.modifiers = modifiers
        self.return_type = return_type
        self.total_args = total_args
        self.throws = throws
        self.calls = calls
        self.loc = loc

    def object_decoder(self, **kwargs):
        ...


class MemberModel(BaseModel):
    def __init__(self, subtype, value):
        super().__init__()

        self.subtype = subtype
        self.value = value

    def object_decoder(self, **kwargs):
        ...


class BodyModel(BaseModel):
    def __init__(self, method, calls):
        super().__init__()

        self.method = method
        self.calls = calls

    def object_decoder(self, **kwargs):
        ...


class ClassModel(BaseModel):
    def __init__(self, name, extends, implements, methods, calls, loc, modifiers=None):
        super().__init__()

        self.modifiers = modifiers
        self.name = name
        self.extends = extends
        self.implements = implements
        self.methods = methods
        self.calls = calls
        self.loc = loc

    def object_decoder(self, **kwargs):
        ...


class InterfaceModel(BaseModel):
    def __init__(self, name, extends, methods, calls, loc, modifiers=None):
        super().__init__()

        self.name = name
        self.extends = extends
        self.methods = methods
        self.calls = calls
        self.loc = loc
        self.modifiers = modifiers

    def object_decoder(self, **kwargs):
        ...


class EnumModel(BaseModel):
    def __init__(self, name, implements, methods, calls, loc, modifiers=None):
        super().__init__()

        self.name = name
        self.implements = implements
        self.methods = methods
        self.calls = calls
        self.loc = loc
        self.modifiers = modifiers

    def object_decoder(self, **kwargs):
        ...


class AnnotationTypeModel(BaseModel):
    def __init__(self, name, calls, loc, modifiers=None):
        super().__init__()

        self.name = name
        self.calls = calls
        self.loc = loc
        self.modifiers = modifiers

    def object_decoder(self, **kwargs):
        ...
