import logging
from argparse import ArgumentParser
from pathlib import Path
from re import Pattern
from re import compile as re_compile
from sys import exit as sys_exit

from yaml import Loader
from yaml import load as load_yaml

from address_file_utils import parse_address
from config_classes import LoaderConfig
from process import process_folder
from service import BlacklistService
from settings import LOG_FORMAT
from settings import LOGGING_LEVEL
from version import get_version


def init_logging():
    handlers: list[logging.StreamHandler] = []
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOGGING_LEVEL)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    logging.basicConfig(level=LOGGING_LEVEL, handlers=handlers)


def main():
    init_logging()
    parser = ArgumentParser(
        prog='File loader, version %s' % get_version(),
        description='Perform files loading and post parsed addresses to Blacklist application',
        usage='python main.py <filename>\n       where filename is YAML configuration file',
    )
    parser.add_argument('filename', help='Configuration file in YAML format')
    config_file = parser.parse_args().filename
    logging.info('Blacklist loader, version: %s', get_version())
    with open(config_file, mode='r') as f:
        config_data: dict = load_yaml(f, Loader=Loader)
    try:
        config = LoaderConfig(**config_data)
    except Exception as e:
        logging.error(f'Error on parsing config file {config_file}, details: {str(e)}')
        sys_exit(1)

    # checking directories
    scan_dir = Path(config.source)
    assert scan_dir.is_dir(), f'Source folder {scan_dir} does not exist'
    archive_dir = Path(config.archive)
    assert archive_dir.is_dir(), f'Archive folder {archive_dir} does not exist'
    reject_dir = Path(config.reject)
    assert reject_dir.is_dir(), f'Reject folder {reject_dir} does not exist'

    # compile rules
    re_compiled: list[Pattern] = [x for x in map(re_compile, map(lambda x: x.pattern, config.rules))]
    # compile file masks
    re_mask_patterns: list[Pattern] = [
        x
        for x in map(
            re_compile,
            map(lambda x: '^' + x.file_mask.replace('.', '\\.').replace('*', '.*') + '$', config.rules),
        )
    ]
    # checking rules on startup
    for re_rule, rule in zip(re_compiled, config.rules):
        if rule.check_value and parse_address(re_rule, rule.check_value) is None:
            logging.error('Error while checking regex rule, no address detected, rule: %s', rule.pattern)
            sys_exit(1)
    # init Blacklist connection service
    service = BlacklistService(config.blacklist)
    process_folder(
        scan_dir, archive_dir, reject_dir, config.rules, re_compiled, re_mask_patterns, service, config.stop_on_error
    )


if __name__ == '__main__':
    main()
