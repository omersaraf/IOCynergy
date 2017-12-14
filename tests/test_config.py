import pytest

import cynergy
from attributes import arguments
from config import Config, Plain, MemoryConfig

FREE_ARGUMENT = "free argument"
PLAIN_ARGUMENT = "plain argument"
CONFIG_ARGUMENT = "config argument"
CONFIG_WITH_DEFAULT = "config with default"
CONFIG_DEFAULT = "default"


@arguments(arg=FREE_ARGUMENT, arg2=Plain(PLAIN_ARGUMENT), arg3=Config(CONFIG_ARGUMENT),
           arg4=Config(CONFIG_WITH_DEFAULT, CONFIG_DEFAULT))
class Example(object):
    def __init__(self, arg: str, arg2: str, arg3: str, arg4: str):
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
    cynergy.initialize(MemoryConfig({CONFIG_ARGUMENT: config_value}))

    instance = cynergy.get(Example)

    assert type(instance) is Example
    assert instance.arg == FREE_ARGUMENT
    assert instance.arg2 == PLAIN_ARGUMENT
    assert instance.arg3 == config_value
    assert instance.arg4 == CONFIG_DEFAULT


def test_argument_not_in_config_and_no_default():
    cynergy.initialize(MemoryConfig({}))

    with pytest.raises(KeyError):
        cynergy.get(ExampleThrow)


def test_config_provider_is_not_initialized():
    cynergy.initialize()

    with pytest.raises(ValueError):
        cynergy.get(Example)
