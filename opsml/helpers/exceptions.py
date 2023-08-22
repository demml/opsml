"""Exception module"""


class MoreThanOnePath(Exception):
    """More than one path found"""


class DirNotFound(ValueError):
    """Directory not found"""


class NotofTypeArray(ValueError):
    """Not of type array"""


class MissingKwarg(ValueError):
    """Kwarg is missing"""


class NotOfCorrectType(ValueError):
    """Not of correct type"""


class SnowFlakeApiError(ValueError):
    """Not of correct type"""


class ServiceNameNotFound(ValueError):
    """Service name not found"""


class NotofTypeDictionary(ValueError):
    """Not of type dictionary"""


class NotofTypeDataFrame(ValueError):
    """Not of type pandas dataframe"""


class LengthMismatch(ValueError):
    """Non-matching length"""


class InvalidDataType(ValueError):
    """Invalid data type"""


class VersionError(ValueError):
    """Invalid version"""
