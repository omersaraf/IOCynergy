import pytest

import iocynergy
from attributes import ioc_arguments
from config import Config, Plain, MemoryConfig

FREE_ARGUMENT = "free argument"
PLAIN_ARGUMENT = "plain argument"
CONFIG_ARGUMENT = "config argument"
CONFIG_WITH_DEFAULT = "config with default"
CONFIG_DEFAULT = "default"


@ioc_arguments(arg=FREE_ARGUMENT, arg2=Plain(PLAIN_ARGUMENT), arg3=Config(CONFIG_ARGUMENT),
               arg4=Config(CONFIG_WITH_DEFAULT, CONFIG_DEFAULT))
class Example(object):
    def __init__(self, arg: str, arg2: str, arg3: str, arg4: str):
        self.arg4 = arg4
        self.arg3 = arg3
        self.arg2 = arg2
        self.arg = arg


@ioc_arguments(arg=Config("not exists key", throw_if_not_exists=True))
class ExampleThrow(object):
    def __init__(self, arg: str):
        self.arg = arg


def test_argument_injection():
    config_value = "config value"
    iocynergy.initialize(MemoryConfig({CONFIG_ARGUMENT: config_value}))

    instance = iocynergy.get(Example)

    assert type(instance) is Example
    assert instance.arg == FREE_ARGUMENT
    assert instance.arg2 == PLAIN_ARGUMENT
    assert instance.arg3 == config_value
    assert instance.arg4 == CONFIG_DEFAULT


def test_argument_not_in_config():
    iocynergy.initialize(MemoryConfig({}))

    with pytest.raises(KeyError):
        iocynergy.get(ExampleThrow)
