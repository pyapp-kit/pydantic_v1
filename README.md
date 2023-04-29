# pydantic_v1

[![CI](https://github.com/pydantic/pydantic/workflows/CI/badge.svg?event=push)](https://github.com/pydantic/pydantic/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/pydantic_v1.svg)](https://pypi.python.org/pypi/pydantic_v1)
[![CondaForge](https://img.shields.io/conda/v/conda-forge/pydantic_v1.svg)](https://anaconda.org/conda-forge/pydantic_v1)
[![versions](https://img.shields.io/pypi/pyversions/pydantic_v1.svg)](https://github.com/pyapp-kit/pydantic_v1)
[![license](https://img.shields.io/github/license/pyapp-kit/pydantic_v1.svg)](https://github.com/pyapp-kit/pydantic_v1/blob/pydantic_v1/LICENSE)

| :warning: Important :warning: |
|----|
| This is a fork of [pydantic](https://github.com/pydantic/pydantic) that is permanently pinned to v1.X.  It will follow all updates of pydantic v1 including and after [v1.10.7](https://pypi.org/project/pydantic/1.10.7/), but will never be updated to v2. It is meant as a "safer" namespace for packages who have not yet had time to upgrade to the pydantic v2 API, and who do not want to risk breakages in an environment that might include a different package that has pinned to pydantic>=2.0 |

For background on why it was felt that this was necessary, see:
https://github.com/pydantic/pydantic/discussions/5402

To use it `pip install pydantic-v1` and then use `import pydantic_v1` wherever you would have used `import pydantic`.

```py
from pydantic_v1 import BaseModel

class User(BaseModel):
    id: int
    name: str = 'John Doe'
```
