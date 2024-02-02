import logging
from argparse import ArgumentParser
from datetime import datetime as dt_datetime
from ipaddress import IPv4Address
from os import listdir
from pathlib import Path
from re import Pattern
from re import compile as re_compile
from sys import exit as sys_exit
from typing import Optional

from requests import JSONDecodeError
from requests import RequestException
from requests import post
from yaml import Loader
from yaml import load as load_yaml

from config_classes import BlackListConnConfig
from config_classes import LoaderConfig
from config_classes import Rule
from settings import CUR_TZ
from settings import LOG_FORMAT
from settings import LOGGING_LEVEL
from version import get_version


def parse_address(pattern: Pattern, file_string) -> Optional[IPv4Address]:
    match = pattern.search(file_string)
    if match:
        # suppose all regular expression is IP address or first matched group if we need more granular filtering
        return IPv4Address(match[1] if len(match.groups()) else match[0])
    return None


def parse_file(file_name: Path, pattern: Pattern) -> set[IPv4Address]:
    """Parse addresses from file"""
    addresses: set[IPv4Address] = set()
    with open(file_name, mode='r') as f:
        file_str = f.readline()
        while file_str:
            address = parse_address(pattern, file_str)
            if address is not None:
                addresses.add(address)
            file_str = f.readline()
    return addresses


def save_addresses(bl_config: BlackListConnConfig, addresses: set[IPv4Address]) -> bool:
    """Save data to blacklist"""
    headers = {}
    if bl_config.token:
        headers['authorization'] = f'Bearer {bl_config.token}'
    data = {
        'source_agent': bl_config.agent_name,
        'action_time': dt_datetime.now(tz=CUR_TZ).strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
        'addresses': [str(x) for x in addresses],
    }
    try:
        response = post(bl_config.uri, headers=headers, json=data)
        response.raise_for_status()
        records_added: int = response.json().get('added')
        logging.info('Successfully added %d records to blacklist application', records_added)
        return False
    except JSONDecodeError as e:
        logging.error('Error while decoding blacklist app response, details: %s', str(e))
    except RequestException as e:
        logging.error('Error while executing request to blacklist application, details: %s', str(e))
    return True


def init_logging():
    handlers: list[logging.StreamHandler] = []
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOGGING_LEVEL)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    logging.basicConfig(level=LOGGING_LEVEL, handlers=handlers)


def process(
    scan_dir: Path,
    archive_dir: Path,
    blacklist: BlackListConnConfig,
    rules: list[Rule],
    re_compiled: list[Pattern],
    re_mask_patterns: list[Pattern],
):
    logging.info('Processing %s', scan_dir)
    for file_name in listdir(scan_dir):
        processed_file = scan_dir.joinpath(file_name)
        if processed_file.is_file():
            logging.info('Processing %s', processed_file)
            for pattern, compiled_pattern, re_filename_pattern in zip(rules, re_compiled, re_mask_patterns):
                if re_filename_pattern.search(file_name):
                    logging.info('Processing file %s with rule %s', processed_file, pattern.pattern)
                    addresses = parse_file(processed_file, compiled_pattern)
                    if addresses:
                        is_error = save_addresses(blacklist, addresses)
                        if is_error:
                            logging.error('Exit now')
                            sys_exit(1)
            # remove processed file
            processed_file.rename(archive_dir.joinpath(file_name))
            logging.info('Moved file %s to archive', processed_file)
    logging.info('Processing complete, exit now')


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
    assert scan_dir.is_dir(), f'Source directory {scan_dir} does not exist'
    archive_dir = Path(config.archive)
    assert archive_dir.is_dir(), f'Archive directory {archive_dir} does not exist'

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
        if rule.check_value:
            if parse_address(re_rule, rule.check_value) is None:
                logging.error('Error while checking regex rule, no address detected, rule: %s', rule.pattern)
                sys_exit(1)
    process(scan_dir, archive_dir, config.blacklist, config.rules, re_compiled, re_mask_patterns)


if __name__ == '__main__':
    main()
