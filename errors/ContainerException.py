from typing import Type


class ContainerException(Exception):
    def __init__(self, cls: Type, message):
        self.cls = cls
        super(ContainerException, self).__init__(message)


class ClassNotFoundException(ContainerException):
    def __init__(self, cls: Type):
        super(ClassNotFoundException, self).__init__(cls,
                                                     'Could not find registered implementation for class: "{}"'.format(
                                                         cls.__name__))


class ConfigProviderRequiredException(ContainerException):
    def __init__(self, cls: Type, argument_name):
        self.cls = cls
        self.argument = argument_name
        super(ConfigProviderRequiredException, self).__init__(cls,
                                                              'The argument "{}" requires config provider for class '
                                                              '"{}" and you did not configure one'.format(argument_name,
                                                                                                          cls.__name__))
