from pydantic import BaseModel


class BlackListConnConfig(BaseModel):
    uri: str  # connection uri (with handle connection path)
    agent_name: str  # agent name for data bundle (passed on every handle call)
    token: str = ''  # connection token (provide if data loading handles are secured with token


class Rule(BaseModel):
    file_mask: str  # file mask for matching files
    pattern: str  # matching pattern with IP address
    check_value: str = ''  # provide example string here for checking regex rule


class LoaderConfig(BaseModel):
    source: str  # source folder
    archive: str  # archive folder
    reject: str  # reject folder
    blacklist: BlackListConnConfig  # Blacklist service connections params
    rules: list[Rule]  # processing rules
    stop_on_error: bool = True  # whether stop on error
