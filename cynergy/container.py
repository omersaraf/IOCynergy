import inspect
import typing
from warnings import warn

from cynergy.config import ConfigProvider, Plain, Config

from cynergy import attributes

T = typing.TypeVar('T')


class __IocContainer(object):
    def __init__(self, config_provider: typing.Optional[ConfigProvider]):
        self.__multiple_class_mapping = {}
        self.__instances = {}
        self.__class_mapping = {}
        self.__config = config_provider
        self.__plain_whitelist = [str, int, dict, list, set, float]

    def __resolve_argument(self, argument):
        if type(argument) in self.__plain_whitelist:
            return argument

        if type(argument) is Plain:
            return argument.value

        if type(argument) is Config:
            if self.__config is None:
                raise ValueError("Tried to access config while ConfigProvider is not initialized")

            if argument.default is None:
                return self.__config.get(argument.value)
            else:
                try:
                    return self.__config.get(argument.value)
                except KeyError:
                    return argument.default

        raise NotImplementedError(
            "Argument type '{}' is not supported (did you pass argument type?)".format(type(argument)))

    def __create_instance_for_single(self, class_to_init: typing.Type, original: typing.Type):
        arguments_mapping = {}
        if hasattr(class_to_init, attributes.IOC_ARGUMENTS_NAME):
            arguments_mapping = getattr(class_to_init, attributes.IOC_ARGUMENTS_NAME)

        arguments = inspect.signature(class_to_init)
        initiated_arguments = {}
        for argument in arguments.parameters.values():
            if argument.name in arguments_mapping:
                initiated_argument = self.__resolve_argument(arguments_mapping[argument.name])
            else:
                initiated_argument = self.get(argument.annotation)

            initiated_arguments[argument.name] = initiated_argument
        self.__set_instance(original, class_to_init(**initiated_arguments))

    def __set_instance(self, cls: typing.Type, instance):
        self.__instances[self.__get_class_name(cls)] = instance

    def __get_instance(self, cls: typing.Type):
        return self.__instances[self.__get_class_name(cls)]

    def __create_instance_for_list(self, cls: typing.Type, original: typing.Type):
        cls = cls.__args__[0]
        classes_to_init = cls if cls.__name__ not in self.__class_mapping else self.__class_mapping[cls.__name__]
        if type(classes_to_init) is not list:
            self.__set_instance(original, [self.get(classes_to_init)])

        else:
            result = []
            for class_to_init in classes_to_init:
                result.append(self.__create_instance(class_to_init))
            self.__set_instance(original, result)

    def __create_instance(self, cls: typing.Type):
        class_to_init = cls if cls.__name__ not in self.__class_mapping else self.__class_mapping[cls.__name__]
        if class_to_init.__name__ is typing.List.__name__:
            self.__create_instance_for_list(class_to_init, cls)
        else:
            self.__create_instance_for_single(class_to_init, cls)
        return self.__get_instance(cls)

    def register_instance(self, cls, instance):
        self.__instances[cls.__name__] = instance

    def register_class(self, cls, assign_to: typing.Type):
        self.__class_mapping[cls.__name__] = assign_to

    def register_many(self, cls, new_classes: typing.List[typing.Type]):
        self.__class_mapping[cls.__name__] = new_classes

    @staticmethod
    def __get_class_name(cls: typing.Type):
        if type(cls) == type(typing.List):
            return cls.__args__[0].__name__
        return cls.__name__

    def get(self, cls: typing.Type[T]) -> T:
        life_cycle = attributes.LifeCycle.SINGLETON
        if hasattr(cls, attributes.LIFECYCLE_ARGUMENT_NAME):
            life_cycle = getattr(cls, attributes.LIFECYCLE_ARGUMENT_NAME)

        if life_cycle == attributes.LifeCycle.SINGLETON:
            if self.__get_class_name(cls) not in self.__instances:
                self.__create_instance(cls)
            return self.__get_instance(cls)
        elif life_cycle == attributes.LifeCycle.MULTI_INSTANCE:
            return self.__create_instance(cls)

        raise NotImplementedError("Not implemented lifecycle", life_cycle)

    def clear_all(self):
        self.__instances = {}


__instance: __IocContainer = None


def __get_instance() -> __IocContainer:
    global __instance
    if __instance is None:
        __instance = __IocContainer(None)
    return __instance


def initialize(config_provider: typing.Optional[ConfigProvider] = None,
               class_mapping: typing.Dict[typing.Type, typing.Type] = None):
    global __instance
    if __instance is not None:
        warn("Container already initialized. It is better to initialize container before using it", UserWarning)
        __instance.clear_all()
    __instance = __IocContainer(config_provider)
    if class_mapping is None:
        return

    for source_class, new_class in class_mapping.items():
        __instance.register_class(source_class, new_class)

def _clear_all():
    return __get_instance().clear_all()

def get(cls: typing.Type[T]) -> T:
    return __get_instance().get(cls)


def register_instance(cls, instance):
    return __get_instance().register_instance(cls, instance)


def register_class(cls, assign_to):
    return __get_instance().register_class(cls, assign_to)


def register_many(cls: typing.Type, types: typing.List[typing.Type]):
    return __get_instance().register_many(cls, types)
