"""Exception module"""


class MoreThanOnePathException(Exception):
    """More than one path found"""


# TODO(@damon): Replace with FileNotFoundError
class DirNotFound(ValueError):
    """Directory not found"""


# TODO(@damon): Replace with TypeError
class NotofTypeArray(ValueError):
    """Not of type array"""


# TODO(@damon): Replace with ArgumentError
class MissingKwarg(ValueError):
    """Kwarg is missing"""


# TODO(@damon): Replace with TypeError
class NotofTypeDictionary(ValueError):
    """Not of type dictionary"""


# TODO(@damon): Replace with TypeError
class NotofTypeDataFrame(ValueError):
    """Not of type pandas dataframe"""


class LengthMismatch(ValueError):
    """Non-matching length"""


# TODO(@damon): Replace with TypeError
class InvalidDataType(ValueError):
    """Invalid data type"""


# TODO(@damon): Replace with ValueError
class VersionError(ValueError):
    """Invalid version"""
