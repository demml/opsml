"""Exception module"""


class MoreThanOnePath(Exception):
    """More than one path found"""


class DirNotFound(ValueError):
    """Directory not found"""


class MissingKwarg(ValueError):
    """Kwarg is missing"""
