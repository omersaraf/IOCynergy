import warnings

import pytest
from cynergy.config import Config, Plain, MemoryConfig, ServiceByName

from cynergy import container
from cynergy.attributes import arguments
from cynergy.errors import ConfigProviderRequiredException

FREE_ARGUMENT = "free argument"
PLAIN_ARGUMENT = "plain argument"
CONFIG_ARGUMENT = "config argument"
CONFIG_WITH_DEFAULT = "config with default"
CONFIG_DEFAULT = "default"

warnings.simplefilter("ignore")


class ExampleInterface(object):
    pass


class ExampleServiceByName(ExampleInterface):
    pass


@arguments(arg=FREE_ARGUMENT, arg2=Plain(PLAIN_ARGUMENT), arg3=Config(CONFIG_ARGUMENT),
           arg4=Config(CONFIG_WITH_DEFAULT, CONFIG_DEFAULT), arg5=ServiceByName("test_service"))
class Example(object):
    def __init__(self, arg: str, arg2: str, arg3: str, arg4: str, arg5: ExampleInterface):
        self.arg5 = arg5
        self.arg4 = arg4
        self.arg3 = arg3
        self.arg2 = arg2
        self.arg = arg


@arguments(arg=Config("not exists key"))
class ExampleThrow(object):
    def __init__(self, arg: str):
        self.arg = arg


def test_argument_injection():
    config_value = "config value"
    container.initialize(MemoryConfig({CONFIG_ARGUMENT: config_value}))
    container.register_instance_by_name("test_service", ExampleServiceByName())

    instance = container.get(Example)

    assert type(instance) is Example
    assert instance.arg == FREE_ARGUMENT
    assert instance.arg2 == PLAIN_ARGUMENT
    assert instance.arg3 == config_value
    assert instance.arg4 == CONFIG_DEFAULT
    assert isinstance(instance.arg5, ExampleServiceByName)


def test_argument_not_in_config_and_no_default():
    container.initialize(MemoryConfig({}))

    with pytest.raises(KeyError):
        container.get(ExampleThrow)


def test_config_provider_is_not_initialized():
    container.initialize()

    with pytest.raises(ConfigProviderRequiredException):
        container.get(Example)
