from dataclasses import dataclass
from pathlib import Path
from typing import Union

from settings import POETRY_CONFIG_FIlE

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from os import getcwd


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int


def load_version(file_name: Union[str, Path]) -> Version:
    current_path = Path(getcwd())
    try:
        with open(current_path.joinpath(file_name), mode='rb') as f:
            config = tomllib.load(f)
        version = config['tool']['poetry']['version']
        parsed_version = version.split('.')
        return Version(major=int(parsed_version[0]), minor=int(parsed_version[1]), patch=int(parsed_version[2]))
    except IOError as e:
        print(f'Error while loading {file_name} file, current_path: {current_path},  details: {str(e)}')
    except tomllib.TOMLDecodeError as e:
        print(f'Error while parsing {file_name} file, details: {str(e)}')
    except ValueError as e:
        print('Error while transforming version info, details: ', str(e))
    except KeyError as e:
        print(f'Error while parsing file - wrong version info record (KeyError), details: {str(e)}')
    # fire exception after catching exceptions
    raise ValueError('Error on obtaining application version')


VERSION_INFO = load_version(POETRY_CONFIG_FIlE)


def get_version():
    return '{}.{}.{}'.format(VERSION_INFO.major, VERSION_INFO.minor, VERSION_INFO.patch)


if __name__ == '__main__':
    print('Application version:', get_version())
