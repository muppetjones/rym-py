# isort: skip_file


try:
    # from . import variation  # noqa
    from .safesort import safesorted
    from ._alias import Alias, resolve_variations  # noqa
    from ._aliasresolver import AliasResolver, resolve_aliases  # noqa
    from ._coerce import Coercer, get_default_coercer
except ImportError:  # pragma: no cover
    raise

try:
    coerce = get_default_coercer()
except Exception:
    import warnings

    warnings.warn("Failed to initialize default Coercer")
    coerce = Coercer(
        converter_resolver=AliasResolver([]),
        value_alias=AliasResolver([]),
    )
