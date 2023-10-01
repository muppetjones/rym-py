# isort: skip_file


try:
    # from . import variation  # noqa
    from .safesort import safesorted  # noqa
    from ._alias import Alias, resolve_variations  # noqa
    from ._aliasfrozen import FrozenAlias  # noqa
    from ._aliasresolver import AliasResolver, resolve_aliases  # noqa

    from ._coerce_errors import CoercionError, InvalidConverterError  # noqa
    from ._coerce_explicit import (  # noqa
        coerce_explicit,
        get_alias_null,
        resolve_type,
    )
    from ._coerce_implicit import coerce_implicit  # noqa
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
