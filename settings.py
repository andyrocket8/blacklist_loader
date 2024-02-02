import logging
from zoneinfo import ZoneInfo

# Set timezone
MSK_TZ = ZoneInfo('Europe/Moscow')
CUR_TZ = MSK_TZ

# Log format
LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
LOGGING_LEVEL = logging.INFO

# Poetry config file name
POETRY_CONFIG_FIlE = 'pyproject.toml'
