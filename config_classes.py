from pydantic import BaseModel


class BlackListConnConfig(BaseModel):
    uri: str
    agent_name: str
    token: str = ''


class Rule(BaseModel):
    file_mask: str
    pattern: str
    check_value: str = ''  # provide example string here for checking regex rule


class LoaderConfig(BaseModel):
    source: str
    archive: str
    blacklist: BlackListConnConfig
    rules: list[Rule]
