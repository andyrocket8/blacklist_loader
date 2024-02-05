# Processing routines
import logging
from ipaddress import IPv4Address
from os import listdir
from pathlib import Path
from re import Pattern
from sys import exit as sys_exit

from address_file_utils import parse_address_file
from config_classes import Rule
from service import Service


def parse_file_with_rules(
    processed_file: Path, rules: list[Rule], re_compiled: list[Pattern], re_mask_patterns: list[Pattern]
) -> tuple[bool, list[set[IPv4Address]]]:
    # parse file with rules. Return list of addresses collected in sets. On one rule we should have 1 item set in list.
    matched = False
    result: list[set[IPv4Address]] = list()
    for pattern, compiled_pattern, re_filename_pattern in zip(rules, re_compiled, re_mask_patterns):
        if re_filename_pattern.search(processed_file.name):
            matched = True
            logging.info('Processing file %s with rule %s', processed_file, pattern.pattern)
            result.append(parse_address_file(processed_file, compiled_pattern))
    return matched, result


def process_file(
    archive_dir: Path,
    reject_dir: Path,
    processed_file: Path,
    rules: list[Rule],
    re_compiled: list[Pattern],
    re_mask_patterns: list[Pattern],
    service: Service,
) -> bool:
    # Parse file with subroutine, call Blacklist service and archive/reject after process
    logging.info('Processing %s', processed_file)
    file_process_error = False
    parsed, addresses_sets = parse_file_with_rules(processed_file, rules, re_compiled, re_mask_patterns)
    if not parsed:
        logging.warning('File %s does not match any rules', processed_file.name)
    for address_set in addresses_sets:
        # iterating over returned list (process every address set). Calculate 'file_process_error'
        file_process_error = service.save_data(address_set) or file_process_error
    if file_process_error:
        # move rejected file to reject folder
        processed_file.rename(reject_dir.joinpath(processed_file.name))
        logging.info('Moved reject file %s to reject folder', processed_file)
    else:
        # archive processed file
        processed_file.rename(archive_dir.joinpath(processed_file.name))
        logging.info('Moved file %s to archive folder', processed_file)
    return file_process_error


def process_folder(
    scan_dir: Path,
    archive_dir: Path,
    reject_dir: Path,
    rules: list[Rule],
    re_compiled: list[Pattern],
    re_mask_patterns: list[Pattern],
    service: Service,
    stop_on_error: bool,
):
    # Process routine (scan folder for files and process rules for every found file)
    logging.info('Processing %s', scan_dir)
    files_list = listdir(scan_dir)
    for file_name in files_list:
        processed_file = scan_dir.joinpath(file_name)
        if processed_file.is_file():
            is_error = process_file(
                archive_dir, reject_dir, processed_file, rules, re_compiled, re_mask_patterns, service
            )
            if is_error and stop_on_error:
                logging.error('Stop on error is ON. Exit now')
                sys_exit(1)
    if len(files_list) == 0:
        logging.info('Folder %s is empty', scan_dir)
    logging.info('Processing complete, exit now')
