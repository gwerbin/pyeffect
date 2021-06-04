import logging
from functools import wraps
from typing import Generic, Tuple, Type, TypeVar

from effects.base import BaseEffect
from effects.utils import parameterized_repr


__all__ = ['FileRead', 'FileWrite', 'RaisedException', 'Raises']


logger = logging.getLogger(__name__)


_IOResult = TypeVar('_IOResult')


class FileRead(BaseEffect, Generic[_IOResult]):
    def __init__(self, openable, mode, *args, **kwargs):
        self.openable = openable
        self.mode = mode
        self.args = args
        self.kwargs = kwargs

        if not self.mode.startswith('r'):
            raise TypeError('FileRead mode must be "r".')


class FileWrite(BaseEffect, Generic[_IOResult]):
    def __init__(self, openable, mode, *args, **kwargs):
        self.openable = openable
        self.mode = mode
        self.args = args
        self.kwargs = kwargs

        if not self.mode[0] in {'w', 'a'}:
            raise TypeError('FileWrite mode must be "w" or "a".')


_Exception = TypeVar('_Exception', bound=Exception)


class RaisedException(BaseEffect, Generic[_Exception]):
    exc: _Exception

    def __init__(self, exc: _Exception):
        self.exc = exc

    def __str__(self):
        return parameterized_repr(self.__class__.__name__, exc=self.exc)


class Raises:
    exception_types: Tuple[Type[Exception], ...]

    def __init__(self, *exc_types: Type[Exception]):
        self.exception_types = tuple(exc_types)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug('Getting result...')
                result = func(*args, **kwargs)
            except self.exception_types as exc:
                logger.debug('Caught an exception; yielding it to be handled: %s', exc)
                yield RaisedException(exc)
            else:
                logger.debug('Got a result; returning it')
                return result
        return wrapper
