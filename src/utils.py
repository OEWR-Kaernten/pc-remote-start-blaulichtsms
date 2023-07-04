import logging
import coloredlogs
import verboselogs
from decouple import config
import requests


class Utilities:
    @staticmethod
    def compare_dict(dict1, dict2):
        output = []
        for key1 in dict1:
            if key1 not in dict2:
                output.append(key1)
        return output

    @staticmethod
    def compare_list(list1, list2):
        return list(set(list1)-set(list2))

    @staticmethod
    def setup_logger(additional_info: str = None):
        logger = verboselogs.VerboseLogger("OrderService")
        logger.addHandler(logging.StreamHandler())
        if additional_info:
            additional_info = f"[{additional_info}]"
        fmt = f"[%(asctime)s] [%(levelname)s] {additional_info or ''}{' ' if additional_info else ''}%(message)s"
        if config("LOG_LEVEL", 2, cast=int) == 0:
            coloredlogs.install(fmt=fmt, logger=logger, level=verboselogs.SPAM)
        elif config("LOG_LEVEL", 2, cast=int) == 1:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.DEBUG)
        elif config("LOG_LEVEL", 2, cast=int) == 2:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.INFO)
        elif config("LOG_LEVEL", 2, cast=int) == 3:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.WARNING)
        elif config("LOG_LEVEL", 2, cast=int) == 4:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.ERROR)

        return logger