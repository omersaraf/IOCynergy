from container import IocContainer


def ioc_arguments(**kwargs):
    def real_decorator(func):
        setattr(func, IocContainer.IOC_ARGUMENTS_NAME, kwargs)
        return func

    return real_decorator


class LifeCycle(object):
    SINGLETON = 0
    MULTI_INSTANCE = 1


def life_cycle(life_cycle_code: int):
    pass
