from pydantic_v1.dataclasses import dataclass


@dataclass
class Foo:
    foo: int


@dataclass(config={})
class Bar:
    bar: str
