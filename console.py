from abc import ABC, abstractmethod
import os
import sys

class Log(ABC):
    @abstractmethod
    def log(self, *args, **kwargs):
        pass


class ConsoleLog(Log):
    def log(self, *args, **kwargs):
        print(*args, **kwargs)


class FileLog(Log):
    def __init__(self, filepath: str):
        self.filepath = filepath
    
    def log(self, *args, **kwargs):
        with open(self.filepath, 'a') as f:
            print(*args, file=f, **kwargs)


class NullLog(Log):
    def log(self, *args, **kwargs):
        pass


class CompositeLog(Log):
    def __init__(self, *loggers: Log):
        self.loggers = loggers
    
    def log(self, *args, **kwargs):
        for logger in self.loggers:
            logger.log(*args, **kwargs)


def create_logger() -> Log:
    
    if sys.stdout.isatty():
        return ConsoleLog()
    
    if os.getenv('LOG_TARGET') == 'file':
        return FileLog('app.log')
    
    return NullLog()


class SLog():
    _loggers: list[Log] = []

    @classmethod
    def register_logger(cls, logger: Log):
        cls._loggers.append(logger)

    @classmethod
    def log(cls, *args, **kwargs):
        for logger in cls._loggers:
            logger.log(*args, **kwargs)