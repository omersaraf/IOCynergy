import inspect
import typing
from warnings import warn

from cynergy.attributes import LifeCycle

from cynergy.config import ConfigProvider, Plain, Config, ServiceByName

from cynergy import attributes
from cynergy.errors.ContainerException import ConfigProviderRequiredException

T = typing.TypeVar('T')


class IocContainer(object):
    def __init__(self, config_provider: typing.Optional[ConfigProvider]):
        self.__multiple_class_mapping = {}
        self.__instances = {}
        self.__class_mapping = {}
        self.__config = config_provider
        self.__primitives = (str, int, dict, list, set, float)
        self.__BY_NAME_FORMAT = "by_name|{}"

    def __resolve_argument(self, argument):
        if type(argument) in self.__primitives:
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

        if type(argument) is ServiceByName:
            return self.get_by_name(argument.value)

        raise NotImplementedError(
            'Argument type "{}" is not supported (did you pass argument type?)'.format(type(argument)))

    def __create_instance_for_single(self, class_to_init: typing.Type, original: typing.Type):
        arguments_mapping = {}
        if hasattr(class_to_init, attributes.IOC_ARGUMENTS_NAME):
            arguments_mapping = getattr(class_to_init, attributes.IOC_ARGUMENTS_NAME)

        try:
            arguments = inspect.signature(class_to_init)
        except Exception:
            raise Exception("Error while trying to access class signature [{}]. Maybe you tried to register a module "
                            "instead of a class?".format(class_to_init.__name__))
        initiated_arguments = {}
        for argument in arguments.parameters.values():
            if argument.name in arguments_mapping:
                try:
                    initiated_argument = self.__resolve_argument(arguments_mapping[argument.name])
                except ValueError:
                    raise ConfigProviderRequiredException(class_to_init, argument)
            else:
                if not argument.default == inspect._empty:
                    initiated_argument = argument.default
                else:
                    if not argument.default == inspect._empty:
                        initiated_argument = argument.default
                    else:
                        if argument.annotation in self.__primitives:
                            raise TypeError("Could not initialize primitive argument [{}] for class [{}] without "
                                            "argument mapping ".format(argument.name, class_to_init.__name__))
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
                result.append(self.get(class_to_init))
            self.__set_instance(original, result)

    def __create_instance(self, cls: typing.Type):
        class_to_init = cls if cls.__name__ not in self.__class_mapping else self.__class_mapping[cls.__name__]
        if class_to_init.__name__ is typing.List.__name__:
            self.__create_instance_for_list(class_to_init, cls)
        else:
            self.__create_instance_for_single(class_to_init, cls)
        return self.__get_instance(cls)

    def register_instance(self, cls, instance):
        self.__register_instance_by_name(cls.__name__, instance)

    def register_class(self, cls, assign_to: typing.Type):
        self.__class_mapping[cls.__name__] = assign_to

    def register_many(self, cls, new_classes: typing.List[typing.Type]):
        self.__class_mapping[cls.__name__] = new_classes

    @staticmethod
    def __get_class_name(cls: typing.Type):
        if type(cls) == type(typing.List):
            return cls.__args__[0].__name__
        return cls.__name__

    def __register_instance_by_name(self, name, instance):
        self.__instances[name] = instance

    def register_instance_by_name(self, name, instance):
        self.__register_instance_by_name(self.__BY_NAME_FORMAT.format(name), instance)

    def get_by_name(self, name):
        key = self.__BY_NAME_FORMAT.format(name)
        if key not in self.__instances:
            KeyError('The service "{}" is not registered'.format(key))
        return self.__instances[key]

    def get(self, cls: typing.Type[T], life_cycle=LifeCycle.SINGLETON) -> T:
        if not life_cycle:
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

    def register(self, cls: typing.Type, class_or_instance):
        if inspect.isclass(class_or_instance):
            self.register_class(cls, class_or_instance)
        else:
            self.register_instance(cls, class_or_instance)


__instance = None


def __get_instance() -> IocContainer:
    global __instance
    if __instance is None:
        __instance = IocContainer(None)
    return __instance


def initialize(config_provider: typing.Optional[ConfigProvider] = None,
               class_mapping: typing.Dict[typing.Type, typing.Type] = None):
    global __instance
    if __instance is not None:
        warn("Container already initialized. If you need multiple instances consider not use the container statically",
             UserWarning)
        __instance.clear_all()
    __instance = IocContainer(config_provider)
    if class_mapping is None:
        return

    for source_class, new_class in class_mapping.items():
        __instance.register_class(source_class, new_class)


def _clear_all():
    return __get_instance().clear_all()


def register_instance_by_name(name, instance):
    return __get_instance().register_instance_by_name(name, instance)


def get(cls: typing.Type[T], life_cycle=LifeCycle.SINGLETON) -> T:
    return __get_instance().get(cls, life_cycle)


def register_instance(cls, instance):
    warn("This function is deprecated, can be now used as register(cls, obj)")
    return __get_instance().register_instance(cls, instance)


def register_class(cls, assign_to):
    """
    Register type (cls) to type assign_to - meaning everytime you'll ask the type cls you'll receive assign_to
    :param cls: Class to map from
    :param assign_to: Class to map to
    """
    warn("This function is deprecated, can be now used as register(cls, obj)")
    return __get_instance().register_class(cls, assign_to)


def register(cls, class_or_instance):
    return __get_instance().register(cls, class_or_instance)


def get_by_name(name):
    return __get_instance().get_by_name(name)


def register_many(cls: typing.Type, types: typing.List[typing.Type]):
    return __get_instance().register_many(cls, types)
