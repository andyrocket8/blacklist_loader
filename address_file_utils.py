from ipaddress import IPv4Address
from pathlib import Path
from re import Pattern
from typing import Optional


def parse_address(pattern: Pattern, file_string) -> Optional[IPv4Address]:
    match = pattern.search(file_string)
    if match:
        # suppose all regular expression is IP address or first matched group if we need more granular filtering
        return IPv4Address(match[1] if len(match.groups()) else match[0])
    return None


def parse_address_file(file_name: Path, pattern: Pattern) -> set[IPv4Address]:
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
