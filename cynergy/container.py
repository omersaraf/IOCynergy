import inspect
from typing import TypeVar, Optional, Type, List, Dict

from warnings import warn

from cynergy.attributes import LifeCycle

from cynergy.config import ConfigProvider, Plain, Config, ServiceByName

from cynergy import attributes
from cynergy.errors.ContainerException import ConfigProviderRequiredException

T = TypeVar('T')


class IocContainer(object):
    def __init__(self, config_provider: Optional[ConfigProvider]):
        self.__multiple_class_mapping = {}
        self.__instances = {}
        self.__class_mapping = {}
        self.__config_cache = {}
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

    def __create_instance_for_single(self, class_to_init: Type, original: Type):
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

    def __set_instance(self, cls: Type, instance):
        self.__instances[self._get_class_name(cls)] = instance

    def __get_instance(self, cls: Type):
        return self.__instances[self._get_class_name(cls)]

    def __create_instance_for_list_new(self, original, classes: List[Type]):
        self.__set_instance(original, [self.get(cls) for cls in classes])

    def __create_instance(self, cls: Type):
        cls_name = self._get_class_name(cls)
        class_to_init = cls if cls_name not in self.__class_mapping else self.__class_mapping[cls_name]
        if isinstance(class_to_init, list):
            self.__create_instance_for_list_new(cls, class_to_init)
        else:
            self.__create_instance_for_single(class_to_init, cls)
        return self.__get_instance(cls)

    def register_instance(self, cls, instance):
        self.__register_instance_by_name(self._get_class_name(cls), instance)

    def register_class(self, cls, assign_to: Type):
        self.__class_mapping[self._get_class_name(cls)] = assign_to

    def register_many(self, cls, new_classes: List[Type]):
        self.__class_mapping[self._get_class_name(List[cls])] = new_classes

    @staticmethod
    def _get_class_name(cls: Type):
        if type(cls) == type(List):
            return 'List[{}]'.format(cls.__args__[0].__name__)
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

    def get(self, cls: Type[T], life_cycle=LifeCycle.SINGLETON) -> T:
        if not life_cycle:
            life_cycle = attributes.LifeCycle.SINGLETON
            if hasattr(cls, attributes.LIFECYCLE_ARGUMENT_NAME):
                life_cycle = getattr(cls, attributes.LIFECYCLE_ARGUMENT_NAME)

        if life_cycle == attributes.LifeCycle.SINGLETON:
            if self._get_class_name(cls) not in self.__instances:
                self.__create_instance(cls)
            return self.__get_instance(cls)
        elif life_cycle == attributes.LifeCycle.MULTI_INSTANCE:
            return self.__create_instance(cls)

        raise NotImplementedError("Not implemented lifecycle", life_cycle)

    def clear_all(self):
        self.__instances = {}

    def register(self, cls: Type, class_or_instance):
        if isinstance(class_or_instance, list):
            self.register_many(cls, class_or_instance)
        elif inspect.isclass(class_or_instance):
            self.register_class(cls, class_or_instance)
        else:
            self.register_instance(cls, class_or_instance)

    def get_config(self, key: str):
        if key not in self.__config_cache:
            self.__config_cache[key] = self.__config.get(key)
        return self.__config_cache[key]


__instance = None


def __get_instance() -> IocContainer:
    global __instance
    if __instance is None:
        __instance = IocContainer(None)
    return __instance


def get_config(key: str):
    return __get_instance().get_config(key)


def initialize(config_provider: Optional[ConfigProvider] = None,
               class_mapping: Dict[Type, Type] = None):
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


def get(cls: Type[T], life_cycle=LifeCycle.SINGLETON) -> T:
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
    return __get_instance().register_class(cls, assign_to)


def register(cls, class_or_instance):
    return __get_instance().register(cls, class_or_instance)


def get_by_name(name):
    return __get_instance().get_by_name(name)


def register_many(cls: Type, types: List[Type]):
    return __get_instance().register_many(cls, types)
