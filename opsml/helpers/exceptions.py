"""Exception module"""


class MoreThanOnePathException(Exception):
    """More than one path found"""


class VersionError(ValueError):
    """Invalid version"""
