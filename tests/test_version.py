import pydantic_v1


def test_version_attribute_is_present():
    assert hasattr(pydantic_v1, '__version__')


def test_version_attribute_is_a_string():
    assert isinstance(pydantic_v1.__version__, str)
