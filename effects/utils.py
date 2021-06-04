import logging
logger = logging.getLogger(__name__)

from typing import Any


def parameterized_repr(caller_name: str, **kwargs: Any) -> str:
    kwarg_str = ', '.join(f'{k}={v!r}' for k, v in kwargs.items())
    return f'{caller_name}({kwarg_str})'
