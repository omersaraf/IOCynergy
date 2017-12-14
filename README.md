# IOCynergy
Python module for IOC container using dependency injection (uses python 3+ type hints)

## Easy way to initialize your services
```python
class TestClass:
    pass
    
class ParentClass:
    def __init__(self, test_class: TestClass):
        self.test_class = test_class

instance = cynergy.get(ParentClass)  # Returns TestClass initialized as singleton

print(type(instance))  # ParentClass
print(type(instance.test_class))  # TestClass
```


## Access to your configuration from any service

```python
@arguments(db=Config('db_name'),host=Config('hostname')
class DbConnector:
    def __init__(self, db: str, host: str):
        self.db = db
        self.host = host

cynergy.initialize(MemoryConfig({
    "db_name": "LocalDbName",
    "hostname": "localhost"
}))

instance = cynergy.get(DbConnector)

print(instance.db)  # LocalDbName
print(instance.host)  # localhost

```
** You can implement your own configuration provider (for exmaple you can create DbConfigProvider which provides your settings from the db)

## Manually register special types

```python
class Original:
    pass
    
class Other:
    pass

cynergy.register_class(Original, Other)

instance = cynergy.get(Original)

print(type(instance))  # Other
```

## Register collection of services
```python
class HandlerBase:
    pass
    
class SomeHandler1(HandlerBase):
    pass
    
class SomeHandler2(HandlerBase):
    pass
    
class SomeService:
    def __init__(self, handlers: List[HandlerBase]):
        self.handlers = handlers

cynergy.register_many(HandlerBase, [SomeHandler1, SomeHandler2])

instance = cynergy.get(SomeService)

print(type(instance.handlers))  # list
print(type(instance.handlers[0]))  # SomeHandler1
print(type(instance.handlers[1]))  # SomeHandler2
```
