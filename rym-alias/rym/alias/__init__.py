# isort: skip_file

try:
    from . import variation  # noqa
    from ._alias import Alias, resolve_variations  # noqa
    from ._aliasresolver import AliasResolver  # noqa
except ImportError:  # pragma: no cover
    raise
