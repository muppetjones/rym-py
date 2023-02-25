# isort: skip_file

try:
    from . import variation  # noqa
    from ._alias import Alias  # noqa
except ImportError:  # pragma: no cover
    raise
