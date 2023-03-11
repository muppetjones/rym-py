# isort: skip_file

try:
    # from . import variation  # noqa
    from ._alias import Alias, resolve_variations  # noqa
    from ._aliasresolver import AliasResolver, resolve_aliases  # noqa
    from ._coerce import Coercer, get_default_coercer
except ImportError:  # pragma: no cover
    raise

coerce = get_default_coercer()
