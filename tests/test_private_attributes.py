from typing import ClassVar, Generic, TypeVar

import pytest

from pydantic_v1 import BaseModel, Extra, PrivateAttr
from pydantic_v1.fields import Undefined
from pydantic_v1.generics import GenericModel


def test_private_attribute():
    default = {'a': {}}

    class Model(BaseModel):
        __foo__ = PrivateAttr(default)

    assert Model.__slots__ == {'__foo__'}
    assert repr(Model.__foo__) == "<member '__foo__' of 'Model' objects>"
    assert Model.__private_attributes__ == {'__foo__': PrivateAttr(default)}

    m = Model()
    assert m.__foo__ == default
    assert m.__foo__ is not default
    assert m.__foo__['a'] is not default['a']

    m.__foo__ = None
    assert m.__foo__ is None

    assert m.dict() == {}
    assert m.__dict__ == {}


def test_private_attribute_factory():
    default = {'a': {}}

    def factory():
        return default

    class Model(BaseModel):
        __foo__ = PrivateAttr(default_factory=factory)

    assert Model.__slots__ == {'__foo__'}
    assert repr(Model.__foo__) == "<member '__foo__' of 'Model' objects>"
    assert Model.__private_attributes__ == {'__foo__': PrivateAttr(default_factory=factory)}

    m = Model()
    assert m.__foo__ == default
    assert m.__foo__ is default
    assert m.__foo__['a'] is default['a']

    m.__foo__ = None
    assert m.__foo__ is None

    assert m.dict() == {}
    assert m.__dict__ == {}


def test_private_attribute_annotation():
    class Model(BaseModel):
        """The best model"""

        __foo__: str

        class Config:
            underscore_attrs_are_private = True

    assert Model.__slots__ == {'__foo__'}
    assert repr(Model.__foo__) == "<member '__foo__' of 'Model' objects>"
    assert Model.__private_attributes__ == {'__foo__': PrivateAttr(Undefined)}
    assert repr(Model.__doc__) == "'The best model'"

    m = Model()
    with pytest.raises(AttributeError):
        m.__foo__

    m.__foo__ = '123'
    assert m.__foo__ == '123'

    m.__foo__ = None
    assert m.__foo__ is None

    del m.__foo__

    with pytest.raises(AttributeError):
        m.__foo__

    m.__foo__ = '123'
    assert m.__foo__ == '123'

    assert m.dict() == {}
    assert m.__dict__ == {}


def test_underscore_attrs_are_private():
    class Model(BaseModel):
        __foo__: str = 'abc'
        __bar__: ClassVar[str] = 'cba'

        class Config:
            underscore_attrs_are_private = True

    assert Model.__slots__ == {'__foo__'}
    assert repr(Model.__foo__) == "<member '__foo__' of 'Model' objects>"
    assert Model.__bar__ == 'cba'
    assert Model.__private_attributes__ == {'__foo__': PrivateAttr('abc')}

    m = Model()
    assert m.__foo__ == 'abc'
    m.__foo__ = None
    assert m.__foo__ is None

    with pytest.raises(ValueError, match='"Model" object has no field "__bar__"'):
        m.__bar__ = 1


def test_private_attribute_intersection_with_extra_field():
    class Model(BaseModel):
        __foo__ = PrivateAttr('private_attribute')

        class Config:
            extra = Extra.allow

    assert Model.__slots__ == {'__foo__'}
    m = Model(__foo__='field')
    assert m.__foo__ == 'private_attribute'
    assert m.__dict__ == m.dict() == {'__foo__': 'field'}

    m.__foo__ = 'still_private'
    assert m.__foo__ == 'still_private'
    assert m.__dict__ == m.dict() == {'__foo__': 'field'}


def test_private_attribute_invalid_name():
    with pytest.raises(
        NameError,
        match='Private attributes "foo" must not be a valid field name; '
        'Use sunder or dunder names, e. g. "_foo" or "__foo__"',
    ):

        class Model(BaseModel):
            foo = PrivateAttr()


def test_slots_are_ignored():
    class Model(BaseModel):
        __slots__ = (
            'foo',
            '_bar',
        )

        def __init__(self):
            super().__init__()
            for attr_ in self.__slots__:
                object.__setattr__(self, attr_, 'spam')

    assert Model.__private_attributes__ == {}
    assert set(Model.__slots__) == {'foo', '_bar'}
    m = Model()
    for attr in Model.__slots__:
        assert object.__getattribute__(m, attr) == 'spam'
        with pytest.raises(ValueError, match=f'"Model" object has no field "{attr}"'):
            setattr(m, attr, 'not spam')


def test_default_and_default_factory_used_error():
    with pytest.raises(ValueError, match='cannot specify both default and default_factory'):
        PrivateAttr(default=123, default_factory=lambda: 321)


def test_config_override_init():
    class MyModel(BaseModel):
        x: str
        _private_attr: int

        def __init__(self, **data) -> None:
            super().__init__(**data)
            self._private_attr = 123

        class Config:
            underscore_attrs_are_private = True

    m = MyModel(x='hello')
    assert m.dict() == {'x': 'hello'}
    assert m._private_attr == 123


def test_generic_private_attribute():
    T = TypeVar('T')

    class Model(GenericModel, Generic[T]):
        value: T
        _private_value: T

        class Config:
            underscore_attrs_are_private = True

    m = Model[int](value=1, _private_attr=3)
    m._private_value = 3
    assert m.dict() == {'value': 1}


def test_private_attribute_multiple_inheritance():
    # We need to test this since PrivateAttr uses __slots__ and that has some restrictions with regards to
    # multiple inheritance
    default = {'a': {}}

    class GrandParentModel(BaseModel):
        __foo__ = PrivateAttr(default)

    class ParentAModel(GrandParentModel):
        pass

    class ParentBModel(GrandParentModel):
        __bar__ = PrivateAttr(default)

    class Model(ParentAModel, ParentBModel):
        __baz__ = PrivateAttr(default)

    assert GrandParentModel.__slots__ == {'__foo__'}
    assert ParentBModel.__slots__ == {'__bar__'}
    assert Model.__slots__ == {'__baz__'}
    assert repr(Model.__foo__) == "<member '__foo__' of 'GrandParentModel' objects>"
    assert repr(Model.__bar__) == "<member '__bar__' of 'ParentBModel' objects>"
    assert repr(Model.__baz__) == "<member '__baz__' of 'Model' objects>"
    assert Model.__private_attributes__ == {
        '__foo__': PrivateAttr(default),
        '__bar__': PrivateAttr(default),
        '__baz__': PrivateAttr(default),
    }

    m = Model()
    assert m.__foo__ == default
    assert m.__foo__ is not default
    assert m.__foo__['a'] is not default['a']

    assert m.__bar__ == default
    assert m.__bar__ is not default
    assert m.__bar__['a'] is not default['a']

    assert m.__baz__ == default
    assert m.__baz__ is not default
    assert m.__baz__['a'] is not default['a']

    m.__foo__ = None
    assert m.__foo__ is None

    m.__bar__ = None
    assert m.__bar__ is None

    m.__baz__ = None
    assert m.__baz__ is None

    assert m.dict() == {}
    assert m.__dict__ == {}
