import logging
from typing import TextIO

from effects import Effectful, FileRead, Raises, handle


def read0(filename, encoding: str = 'utf-8') -> str:
    with open(filename, encoding=encoding) as f:
        return f.read()


@Raises(OSError)
def read1(filename, encoding: str = 'utf-8') -> str:
    with open(filename, encoding=encoding) as f:
        return f.read()


# #def read_file(filename, encoding: str = 'utf-8') -> Effectful[FileIO, IO, str]:
def read2(filename, encoding: str = 'utf-8') -> Effectful[FileRead, TextIO, str]:
    with (yield FileRead(filename, 'r', encoding=encoding)) as f:
        return f.read()


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(module)s:%(funcName)s:%(message)s'
)

# Unhandled i/o, handled exception
try:
    print( handle(read1('foo.txt')) )
    print( handle(read1('bar.txt')) )
except FileNotFoundError as exc:
    print('Top-level exception:', exc)

# Handled i/o, handled exception
try:
    print( handle(read2('foo.txt')) )
    print( handle(read2('bar.txt')) )
except FileNotFoundError as exc:
    print('Top-level exception:', exc)
