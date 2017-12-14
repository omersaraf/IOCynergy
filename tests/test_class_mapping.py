import iocynergy
from config import MemoryConfig


class Example(object):
    pass


class Example2(object):
    pass


def test_class_mapping():
    iocynergy.initialize(MemoryConfig({}))
    iocynergy.register_class(Example, Example2)

    instance = iocynergy.get(Example)

    assert type(instance) is Example2


def test_class_mapping_from_init():
    iocynergy.initialize(MemoryConfig({}), {Example: Example2})

    instance = iocynergy.get(Example)

    assert type(instance) is Example2
