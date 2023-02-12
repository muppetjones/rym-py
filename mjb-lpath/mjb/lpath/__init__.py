# isort: skip_file

try:
    from ._delim import get_delimiter, reset_delimiter, set_delimiter, _DELIMITER
    from ._get import get  # noqa
    from ._set import set  # noqa
except ImportError:
    raise
