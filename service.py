import logging
from abc import ABC
from abc import abstractmethod
from datetime import datetime as dt_datetime
from ipaddress import IPv4Address

from requests import JSONDecodeError
from requests import RequestException
from requests import post

from config_classes import BlackListConnConfig
from settings import CUR_TZ


class Service(ABC):
    # Interface for calling blacklist service
    @abstractmethod
    def save_data(self, addresses: set[IPv4Address]) -> bool:
        # implement service interaction here. Returns True if error occurs.
        pass


class BlacklistService(Service):
    def __init__(self, bl_config: BlackListConnConfig):
        self.bl_config = bl_config

    def save_data(self, addresses: set[IPv4Address]) -> bool:
        """Save data to blacklist"""
        headers = {}
        if self.bl_config.token:
            headers['authorization'] = f'Bearer {self.bl_config.token}'
        data = {
            'source_agent': self.bl_config.agent_name,
            'action_time': dt_datetime.now(tz=CUR_TZ).strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'addresses': [str(x) for x in addresses],
        }
        try:
            response = post(self.bl_config.uri, headers=headers, json=data)
            response.raise_for_status()
            records_added: int = response.json().get('added')
            logging.info('Successfully added %d records to blacklist application', records_added)
            return False
        except JSONDecodeError as e:
            logging.error('Error while decoding blacklist app response, details: %s', str(e))
        except RequestException as e:
            logging.error('Error while executing request to blacklist application, details: %s', str(e))
        return True
