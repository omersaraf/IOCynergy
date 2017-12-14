from typing import List

import cynergy


class Example(object):
    pass


class Example1(object):
    pass


class Example2(object):
    pass


def test_register_multiple():
    cynergy.register_many(Example, [Example1, Example2])
    instance = cynergy.get(List[Example])

    assert type(instance) is list
    assert len(instance) == 2
    assert type(instance[0]) is Example1
    assert type(instance[1]) is Example2
