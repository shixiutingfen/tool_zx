# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

"""
Sloth exception classes.
"""


class ImproperlyConfigured(Exception):
    """There is an error in the configuration."""
    pass


class NotImplementedException(Exception):
    """This function/method/class has not been implemented yet."""
    pass


class InvalidArgumentException(Exception):
    """The argument is invalid."""
    pass
