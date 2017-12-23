import warnings

import cynergy


warnings.simplefilter("ignore", UserWarning)


class Example(object):
    pass


class Example2(object):
    pass


def setup():
    cynergy.initialize()


def test_class_mapping():
    cynergy.initialize()
    cynergy.register_class(Example, Example2)

    instance = cynergy.get(Example)

    assert type(instance) is Example2


def test_class_mapping_from_init():
    cynergy.initialize(class_mapping={Example: Example2})

    instance = cynergy.get(Example)

    assert type(instance) is Example2
