IOC_ARGUMENTS_NAME = '__ioc_arguments__'
LIFECYCLE_ARGUMENT_NAME = '__lifecycle__'


def arguments(**kwargs):
    def real_decorator(func):
        setattr(func, IOC_ARGUMENTS_NAME, kwargs)
        return func

    return real_decorator


class LifeCycle(object):
    SINGLETON = 0
    MULTI_INSTANCE = 1


def life_cycle(life_cycle_code: int):
    def real_decorator(func):
        setattr(func, LIFECYCLE_ARGUMENT_NAME, life_cycle_code)
        return func

    return real_decorator
