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


class MemoryConfig(ConfigProvider):
    def __init__(self, config: Dict[str, Any]):
        self.__config = config

    def get(self, key: str) -> Any:
        return self.__config[key]


class ModuleConfig(ConfigProvider):
    def __init__(self, module):
        self.module = module

    def get(self, key: str) -> Any:
        return getattr(self.module, key)
