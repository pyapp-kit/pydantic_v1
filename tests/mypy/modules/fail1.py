"""
Test mypy failure with missing attribute
"""
from datetime import datetime
from typing import List, Optional

from pydantic_v1 import BaseModel, NoneStr
from pydantic_v1.types import Json


class Model(BaseModel):
    age: int
    first_name = 'John'
    last_name: NoneStr = None
    signup_ts: Optional[datetime] = None
    list_of_ints: List[int]
    json_list_of_ints: Json[List[int]]


m = Model(age=42, list_of_ints=[1, '2', b'3'])

print(m.age + 'not integer')
m.json_list_of_ints[0] + 'not integer'
