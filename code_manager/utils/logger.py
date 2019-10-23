import sys
import os
import logging
import logging.handlers
import datetime


RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RED = '\033[38;5;197m'

logging.VERBOSE = 5


class ShutdownHandler(logging.Handler):
    def emit(self, record):
        logging.shutdown()
        sys.exit(1)


def setup_logging(args, opt):
    assert args is not None
    assert opt is not None

    logging.getLogger().handlers = []

    logger = logging.getLogger()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.VERBOSE)
    else:
        logger.setLevel(logging.INFO)

    if 'Logging' in opt.keys() and 'direcory' in opt['Logging']:

        path_to_log_directory = opt['Logging']['Direcory']
        if not os.path.exists(path_to_log_directory):
            os.makedirs(path_to_log_directory)

        # Rotating file logging
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        log_filename = datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
        log_filename = os.path.join(path_to_log_directory, log_filename)

        rot = logging.handlers.RotatingFileHandler(log_filename, maxBytes=100 * 1024 * 1024, backupCount=10)
        rot.setLevel(logging.VERBOSE)
        rot.setFormatter(formatter)
        logger.addHandler(rot)

    # Info Logging
    formatter = logging.Formatter('{1}%(asctime)s{2} [{0}%(levelname)s{2}] %(message)s'.format(CYAN, GREEN, RESET))
    sh_info = logging.StreamHandler(sys.stdout)
    sh_info.setFormatter(formatter)
    logger.addHandler(sh_info)

    # Exit on CRITICAL
    logger.addHandler(ShutdownHandler(level=50))


def info_blue(msg, *args):
    logging.info(BLUE + msg + RESET, *args)


def debug_cyan(msg, *args):
    logging.debug(CYAN + msg + RESET, *args)


def debug_red(msg, *args):
    logging.debug(RED + msg + RESET, *args)
