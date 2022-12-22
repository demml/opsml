"""Exception module"""


class MoreThanOnePath(Exception):
    """More than one path found"""


class DirNotFound(ValueError):
    """Directory not found"""


class MissingKwarg(ValueError):
    """Kwarg is missing"""


class NotOfCorrectType(ValueError):
    """Not of correct type"""


class ServiceNameNotFound(ValueError):
    """Service name not found"""
