# dotenv-azd

[![PyPI - Version](https://img.shields.io/pypi/v/dotenv-azd.svg)](https://pypi.org/project/dotenv-azd)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dotenv-azd.svg)](https://pypi.org/project/dotenv-azd)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install dotenv-azd
```

## Usage

```
from dotenv_azd import load_azd_env
from os import getenv

load_azd_env()
print(getenv('AZURE_ENV_NAME'))
```

## License

`dotenv-azd` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
