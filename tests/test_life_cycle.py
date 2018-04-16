from typing import Type

from cynergy import container
from cynergy.attributes import life_cycle, LifeCycle


@life_cycle(LifeCycle.MULTI_INSTANCE)
class MultiExample(object):
    count = 0

    def __init__(self):
        MultiExample.count += 1


@life_cycle(LifeCycle.SINGLETON)
class SingleExample(object):
    count = 0

    def __init__(self):
        SingleExample.count += 1


class NoLifeCycleExample(object):
    count = 0

    def __init__(self):
        NoLifeCycleExample.count += 1


def test_multi():
    assert_instance_of(MultiExample, 2)


def test_single():
    assert_instance_of(SingleExample, 1)


def test_no_lifecycle():
    assert_instance_of(NoLifeCycleExample, 1)


def assert_instance_of(cls: Type, expected_count):
    container.get(cls)
    container.get(cls)

    assert cls.count == expected_count
