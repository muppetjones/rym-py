# `rym-py`

[![CI](https://github.com/muppetjones/rym-py/actions/workflows/ci.yaml/badge.svg)](https://github.com/muppetjones/rym-py/actions/workflows/ci.yaml)

A collection of python packages to support various, quirky features.
These tools are intended to reduce reduncancy and complexity but mostly
-- and more importantly -- make your code more compatible. Whether
backwards-compatible with your own systems or cross-compatible with
multiple different packages or package versions.

## Packages

- `rym-alias`
  - [![PyPI - Version](https://img.shields.io/pypi/v/rym-alias.svg)](https://pypi.org/project/rym-alias)
  - [Documentation](https://muppetjones.github.io/rym-py/rym-alias)

- `rym-cx`
  - [![PyPI - Version](https://img.shields.io/pypi/v/rym-cx.svg)](https://pypi.org/project/rym-cx)
  - [Documentation](https://muppetjones.github.io/rym-py/rym-cx)

- `rym-lpath`
  - [![PyPI - Version](https://img.shields.io/pypi/v/rym-lpath.svg)](https://pypi.org/project/rym-lpath)
  - [Documentation](https://muppetjones.github.io/rym-py/rym-lpath)

- `rym-token`
  - [![PyPI - Version](https://img.shields.io/pypi/v/rym-token.svg)](https://pypi.org/project/rym-token)
  - [Documentation](https://muppetjones.github.io/rym-py/rym-token)

## Known Issuse

### Running `tox` within the `rym-*` subdirectory

In order to keep run tox from a subdirectory, we need to symlink the tox.ini.
Otherwise, tox will find the config file at the root and try to use the pyproject.toml
from root instead of from the subdir.

```bash
cd rym-lpath
ln -s ../tox.ini tox.ini
```

This allows each subpackage can run tox locally and find its own configuration
while we can maintain a single source of truth for the tox configuration.
I.e., changes to tox.ini automatically apply to all subpackages.

However, if the tox configuration ever needs to be different between subpackages
(different test environments, different dependencies, etc.), we'll to either:

- Break out into separate tox.ini files for those packages, or
- Use tox's inheritance features to have package-specific overrides