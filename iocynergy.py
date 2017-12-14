import inspect
from typing import Type, Dict, List, Any

from attributes import LifeCycle, LIFECYCLE_ARGUMENT_NAME, IOC_ARGUMENTS_NAME
from config import ConfigProvider, Plain, Config


class IocContainer(object):
    def __init__(self, config_provider: ConfigProvider):
        self.__multiple_class_mapping = {}
        self.__instances = {}
        self.__class_mapping = {}
        self.__config = config_provider

    def __resolve_argument(self, argument):
        if type(argument) in IocContainer.PLAIN_WHITELIST:
            return argument

        if type(argument) is Plain:
            return argument.value

        if type(argument) is Config:
            if argument.throw_if_not_exists:
                return self.__config.get(argument.value)
            else:
                try:
                    return self.__config.get(argument.value)
                except KeyError:
                    return argument.default

        raise NotImplementedError(
            "Argument type '{}' is not supported (did you pass argument type?)".format(type(argument)))

    PLAIN_WHITELIST = [str, int, dict, list, set, float]

    def __create_instance_for_single(self, class_to_init: Type):
        arguments_mapping = {}
        if hasattr(class_to_init, IOC_ARGUMENTS_NAME):
            arguments_mapping = getattr(class_to_init, IOC_ARGUMENTS_NAME)

        arguments = inspect.signature(class_to_init)
        initiated_arguments = {}
        for argument in arguments.parameters.values():
            if argument.name in arguments_mapping:
                initiated_argument = self.__resolve_argument(arguments_mapping[argument.name])
            else:
                initiated_argument = self.get(argument.annotation)

            initiated_arguments[argument.name] = initiated_argument
        return class_to_init(**initiated_arguments)

    def __create_instance_for_list(self, cls: Type) -> List:
        cls = cls.__args__[0]
        classes_to_init = cls if cls.__name__ not in self.__class_mapping else self.__class_mapping[cls.__name__]
        if type(classes_to_init) is not list:
            return [self.get(classes_to_init)]

        else:
            result = []
            for class_to_init in classes_to_init:
                result.append(self.__create_instance(class_to_init))
            return result

    def __create_instance(self, cls: Type):
        class_to_init = cls if cls.__name__ not in self.__class_mapping else self.__class_mapping[cls.__name__]
        if class_to_init.__name__ is List.__name__:
            return self.__create_instance_for_list(class_to_init)
        return self.__create_instance_for_single(class_to_init)

    def register_instance(self, cls, instance):
        self.__instances[cls.__name__] = instance

    def register_class(self, cls, assign_to):
        self.__class_mapping[cls.__name__] = assign_to

    def register_many(self, cls, new_classes: List[Type]):
        self.__class_mapping[cls.__name__] = new_classes

    def get(self, cls: Type):
        life_cycle = LifeCycle.SINGLETON
        if hasattr(cls, LIFECYCLE_ARGUMENT_NAME):
            life_cycle = getattr(cls, LIFECYCLE_ARGUMENT_NAME)

        if life_cycle == LifeCycle.SINGLETON:
            if cls.__name__ not in self.__instances:
                self.__instances[cls.__name__] = self.__create_instance(cls)

            return self.__instances[cls.__name__]

        elif life_cycle == LifeCycle.MULTI_INSTANCE:
            return self.__create_instance(cls)

        raise NotImplementedError("Not implemented lifecycle", life_cycle)

_instance: IocContainer = None


def initialize(config_provider: ConfigProvider, class_mapping: Dict[Type, Type] = None):
    """

    :rtype: object
    """
    global _instance
    _instance = IocContainer(config_provider)
    if class_mapping is None:
        return

    for source_class, new_class in class_mapping.items():
        _instance.register_class(source_class, new_class)


def get(cls: Type) -> Any:
    return _instance.get(cls)


def register_instance(cls, instance):
    return _instance.register_instance(cls, instance)


def register_class(cls, assign_to):
    return _instance.register_class(cls, assign_to)


def register_many(cls: Type, types: List[Type]):
    return _instance.register_many(cls, types)
