import warnings

from cynergy import container


warnings.simplefilter("ignore", UserWarning)


class Example(object):
    pass


class Example2(object):
    pass


def setup():
    container.initialize()


def test_class_mapping():
    container.initialize()
    container.register_class(Example, Example2)

    instance = container.get(Example)

    assert type(instance) is Example2


def test_class_mapping_from_init():
    container.initialize(class_mapping={Example: Example2})

    instance = container.get(Example)

    assert type(instance) is Example2
