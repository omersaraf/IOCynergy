import cynergy
from config import MemoryConfig


class Example(object):
    pass


class Example2(object):
    pass


def test_class_mapping():
    cynergy.initialize(MemoryConfig({}))
    cynergy.register_class(Example, Example2)

    instance = cynergy.get(Example)

    assert type(instance) is Example2


def test_class_mapping_from_init():
    cynergy.initialize(MemoryConfig({}), {Example: Example2})

    instance = cynergy.get(Example)

    assert type(instance) is Example2
