import logging
logger = logging.getLogger(__name__)

from typing import Callable, Dict, Generator, IO, Mapping, NoReturn, Type, TypeVar, Union, overload

from effects.base import BaseEffect, Effectful, NotAnEffect, UnhandledEffect
from effects.effects import Raises, FileRead, FileWrite, RaisedException


__all__ = ['handle']


_IOResult = TypeVar('_IOResult', str, bytes)


@Raises(OSError)
def _default_handle_file_read(effect: FileRead[_IOResult]) -> IO[_IOResult]:
    logger.debug('Handling file i/o: %s', effect)
    return open(effect.openable, effect.mode, *effect.args, **effect.kwargs)


@Raises(OSError)
def _default_handle_file_write(effect: FileWrite[_IOResult]) -> IO[_IOResult]:
    logger.debug('Handling file i/o: %s', effect)
    return open(effect.openable, effect.mode, *effect.args, **effect.kwargs)


def _default_handle_raised_exception(effect: RaisedException) -> NoReturn:
    logger.debug('Handling raised exception: %s', effect)
    raise effect.exc


_Effect = TypeVar('_Effect', bound=BaseEffect)
_Continuation = TypeVar('_Continuation', covariant=True)
_OperationReturn = TypeVar('_OperationReturn', covariant=True)
_Other = TypeVar('_Other')  # Anything else; TODO: how to specify "not Effectful"?


Handler = Callable[[BaseEffect], _Continuation]


_default_handlers: Dict[Type[BaseEffect], Handler] = {
    FileRead: _default_handle_file_read,
    FileWrite: _default_handle_file_write,
    RaisedException: _default_handle_raised_exception,
}


def _handle_impl(
    operation: Effectful[_Effect, _Continuation, _OperationReturn],
    handlers: Mapping[Type[BaseEffect], Handler] = _default_handlers
) -> _OperationReturn:
    handler_types = tuple(handlers.keys())

    send_value = None
    while True:
        try:
            if send_value is None:
                result = next(operation)
            else:
                result = operation.send(send_value)
        except StopIteration as exc:
            return(exc.value)

        if not isinstance(result, BaseEffect):
            raise NotAnEffect(result)
        if not isinstance(result, handler_types):
            raise UnhandledEffect(result)

        h = handlers[type(result)]
        send_value = handle(h(result), handlers=handlers)


@overload
def handle(
    operation: Effectful[_Effect, _Continuation, _OperationReturn],
    handlers: Mapping[Type[BaseEffect], Handler] = _default_handlers
) -> _OperationReturn:
    ...

@overload
def handle(
    operation: _Other,
    handlers: Mapping[Type[BaseEffect], Handler] = _default_handlers
) -> _Other:
    ...

def handle(operation, handlers):
    if not isinstance(operation, Effectful):
        logger.debug('Operation is not something that can be handled; return as-is.')
        return operation
    else:
        return _handle_impl(operation, handlers)
