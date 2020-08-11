import logging
import logging.config
import time
from functools import wraps
import sys
sys.path.append('./utils')
sys.path.append('./conf')
sys.path.append('./common')
import redis 
from redis import RedisError


class LoggerManager:
    """
    This class has the generic Logging utility
    -- It takes in the LoggerName and returns the instance of the logger

    """

    def __init__(self, logger_name, log_level=None):
        logging.config.fileConfig("../conf/logging.conf")
        self.logger = logging.getLogger(logger_name)
        self.logger.info('creating an instance of the Logger {}'.format(logger_name))
        self.log_level = log_level

    def get_logger(self):
        '''
        get the logger initialized
        '''
        return self.logger

    def set_logger_level(self, log_level):
        '''
        set the log level
        '''
        self.log_level = log_level


def _truncate_arg(arg):
    if isinstance(arg, (int, float, bool)):
        return arg
    elif isinstance(arg, str):
        return arg[:255] + (arg[255:] and '...')
    else:
        return str(type(arg).__name__)


def log_function_runtime(exec_time_record=None):
    def wrapper(orig_func):
        func_runtime_logger = LoggerManager("FileAnalyzerAPILogger").get_logger()
        def wrapped_func(*args, **kwargs):
            start = int(time.time()) * 1000
            result = orig_func(*args, **kwargs)
            run_time = (int(time.time()) * 1000) - start
            func_runtime_logger.info('Function: {} execution time: {}ms'.format(
                orig_func.__qualname__, run_time))
            if exec_time_record is not None and isinstance(exec_time_record, list):
                func_data = {
                    'name': orig_func.__qualname__,
                    'run_time_ms': run_time,
                    'args': {
                        str(i): _truncate_arg(args[i]) for i in range(len(args))
                    },
                    'kwargs': {
                        str(k): _truncate_arg(kwargs[k]) for k in kwargs
                    }
                }
                exec_time_record.append(func_data)
            return result

        return wrapped_func

    return wrapper


def log_enter_and_exit(orig_func):
    logger = LoggerManager("FileAnalyzerAPILogger").get_logger()
    @wraps(orig_func)
    def wrapped(*args, **kwargs):
        func_full_name = '.'.join(
            [orig_func.__module__, orig_func.__qualname__])
        logger.debug('[started executing -] {}'.format(func_full_name))
        start = int(time.time()) * 1000
        result = orig_func(*args, **kwargs)
        run_time = (int(time.time()) * 1000) - start
        logger.debug('[stopped executing] {} (Execution time: {}ms)'.format(
            func_full_name, run_time))
    return wrapped

