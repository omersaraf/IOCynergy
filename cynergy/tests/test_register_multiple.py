from typing import List

from cynergy import container


class Example(object):
    pass


class Example1(object):
    pass


class Example2(object):
    pass


class Example3(object):
    pass


class Example4(object):
    pass


class Main(object):
    def __init__(self, examples: List[Example], examples1: List[Example1]):
        self.examples1 = examples1
        self.examples = examples


class Main2(object):
    def __init__(self, examples: List[Example]):
        self.examples = examples


def test_register_multiple():
    container.initialize()
    container.register_many(Example, [Example1, Example2])
    instance = container.get(List[Example])

    assert type(instance) is list
    assert len(instance) == 2
    assert type(instance[0]) is Example1
    assert type(instance[1]) is Example2


def test_multiple_list_arguments():
    container._clear_all()
    container.register_many(Example, [Example2, Example3])
    container.register_many(Example1, [Example3, Example4])

    instance = container.get(Main)

    assert type(instance) is Main
    assert len(instance.examples) == 2
    assert len(instance.examples1) == 2
    assert type(instance.examples[0]) is Example2
    assert type(instance.examples[1]) is Example3
    assert type(instance.examples1[0]) is Example3
    assert type(instance.examples1[1]) is Example4


class MainWrapper(object):
    def __init__(self, main: Main):
        self.main = main


def test_multiple_list_arguments_with_wrap():
    container._clear_all()
    container.register_many(Example, [Example2, Example3])
    container.register_many(Example1, [Example3, Example4])

    instance = container.get(MainWrapper)

    assert type(instance) is MainWrapper
    assert len(instance.main.examples) == 2
    assert len(instance.main.examples1) == 2
    assert type(instance.main.examples[0]) is Example2
    assert type(instance.main.examples[1]) is Example3
    assert type(instance.main.examples1[0]) is Example3
    assert type(instance.main.examples1[1]) is Example4


def test_register_multiple_when_onc_instance_is_already_registered():
    container._clear_all()
    ex1 = Example2()
    container.register(Example1, ex1)
    container.register_many(Example, [Example1, Example3])

    instance = container.get(Main2)

    assert type(instance) is Main2
    assert len(instance.examples) == 2
    assert instance.examples[0] == ex1
    assert type(instance.examples[1]) is Example3
