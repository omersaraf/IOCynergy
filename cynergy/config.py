from typing import Any, Dict


class IocArgumentInitiator(object):
    def __init__(self, value):
        self.value = value


class Config(IocArgumentInitiator):
    def __init__(self, value, default=None):
        super().__init__(value)
        self.default = default


class Plain(IocArgumentInitiator):
    pass


class ServiceByName(IocArgumentInitiator):
    def __init__(self, value):
        super().__init__(value)


class ConfigProvider(object):
    def get(self, key: str) -> Any:
        raise NotImplementedError("Not implemented")

    def set(self, key: str, value: Any):
        raise NotImplementedError("Not implemented")


class MemoryConfig(ConfigProvider):
    def __init__(self, config: Dict[str, Any]):
        self.__config = config

    def set(self, key: str, value: Any):
        self.__config[key] = value

    def get(self, key: str) -> Any:
        return self.__config[key]
