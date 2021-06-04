import logging
logger = logging.getLogger(__name__)

import sys
from functools import wraps
from typing import (
    Any,
    Generator,
    Generic,
    IO,
    List,
    NoReturn,
    Sequence,
    Tuple,
    Type,
    TypeVar
)


__all__ = ['BaseEffect', 'NotAnEffect', 'UnhandledEffect', 'Effectful']


_T = TypeVar('_T')


class BaseEffect:
    def __str__(self):
        return self.__class__.__name__


class NotAnEffect(Exception):
    value: Any

    def __init__(self, value: BaseEffect):
        super().__init__(value)
        self.value = value

    def __str__(self):
        return str(self.value)


class UnhandledEffect(Exception):
    effect: BaseEffect

    def __init__(self, effect: BaseEffect):
        super().__init__(effect)
        self.effect = effect

    def __str__(self):
        return str(self.effect)


Effectful = Generator

