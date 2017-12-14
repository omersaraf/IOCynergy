import cynergy
from config import MemoryConfig


class Hierarchy0(object):
    pass


class Hierarchy10(object):
    def __init__(self, arg: Hierarchy0):
        self.arg = arg


class Hierarchy11(object):
    def __init__(self, arg: Hierarchy0):
        self.arg = arg


class Hierarchy2(object):
    def __init__(self, arg1: Hierarchy10, arg2: Hierarchy11):
        self.arg1 = arg1
        self.arg2 = arg2


class Hierarchy3(object):
    def __init__(self, arg1: Hierarchy10, arg2: Hierarchy2):
        self.arg2 = arg2
        self.arg1 = arg1


def assert_type(instance, cls):
    assert type(instance) is cls
    assert instance is not None


def test_recursive_injection():
    cynergy.initialize(MemoryConfig({}))

    instance = cynergy.get(Hierarchy3)

    assert_type(instance, Hierarchy3)
    assert_type(instance.arg1, Hierarchy10)
    assert_type(instance.arg2, Hierarchy2)
    assert_type(instance.arg1.arg, Hierarchy0)
    assert_type(instance.arg2.arg1, Hierarchy10)
    assert_type(instance.arg2.arg2, Hierarchy11)
    assert_type(instance.arg2.arg2.arg, Hierarchy0)
    assert_type(instance.arg2.arg2.arg, Hierarchy0)
