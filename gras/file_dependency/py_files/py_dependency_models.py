from abc import ABCMeta, abstractmethod


class BaseModel(metaclass=ABCMeta):
    """
    Base Class for all python dependency models
    """

    def __init__(self):
        pass

    @abstractmethod
    def object_decoder(self, **kwargs):
        """
        Object Decoder takes the dictionary of arguments and inserts the key value pairs into an object of the
        specified model
        """
        pass


class ProjectStatsModel(BaseModel):
    """
    The class represents the basic statistics of a project

    :param file_count: total number of files in the project
    :type file_count: int

    :param class_count: total number of classes in the project
    :type class_count: int

    :param dependency_count: total number of dependencies in the project
    :type dependency_count: int

    :param total_loc: total lines of code in the project
    :type total_loc: int
    """

    def __init__(self, file_count, class_count, dependency_count, total_loc):
        """Constructor Method"""
        super().__init__()
        self.file_count = file_count
        self.class_count = class_count
        self.dependency_count = dependency_count
        self.total_loc = total_loc

    def object_decoder(self, dic):
        """
        Object decoder function for :class:`ProjectStatsModel`

        :param dic: dictionary containing the dependency model data
        :type dic: dict

        :return: :class:`ProjectStatsModel` object
        :rtype: object
        """
        obj = ProjectStatsModel(
            file_count=dic["file_count"],
            total_loc=dic["total_loc"],
            class_count=dic["class_count"],
            dependency_count=dic["dependency_count"]
            # TODO:this is external dependencys only, I think counting imports for every file isnt useful/ add more
            #  stuff later
            )
        return obj


class FileStatsModel(BaseModel):
    """
    The class represents the basic statistics of a file in a project

        :param file_name: name of the file
        :type file_name: str

        :param import_count: number of imports
        :type import_count: int

        :param imported_by_count: number of times the file has been imported
        :type imported_by_count: int

        :param class_count: number of classes in the file
        :type class_count: int

        :param var_count: number of variables in the file
        :type var_count: int

        :param func_count: number of functions in the file
        :type func_count: int

        :param loc: total lines of code in the file
        :type loc: int
    """

    def __init__(self,file_id, file_name, import_count, imported_by_count, class_count, var_count, func_count, loc):
        """Constructor Method"""
        super().__init__()
        self.file_id = file_id
        self.file_name = file_name
        self.import_count = import_count
        self.imported_by_count = imported_by_count
        self.class_count = class_count
        self.var_count = var_count
        self.func_count = func_count
        self.loc = loc

    def object_decoder(self, dic):
        """
        Object decoder function for :class:`ProjectStatsModel`

        :param dic: dictionary containing the dependency model data
        :type dic: dict

        :return: :class:`ProjectStatsModel` object
        :rtype: object
        """

        obj = FileStatsModel(
            file_id=dic["file_id"],
            file_name=dic["file_name"],
            import_count=dic["import_count"],
            imported_by_count=dic["imported_by_count"],
            class_count=dic["class_count"],
            var_count=dic["var_count"],
            func_count=dic["func_count"],
            loc=dic["loc"]
            )
        return obj
