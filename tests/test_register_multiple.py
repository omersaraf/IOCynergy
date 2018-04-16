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


def test_register_multiple():
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
