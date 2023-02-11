# isort: skip_file

try:
    from ._delim import get_delimiter, reset_delimiter, set_delimiter, _DELIMITER
    from ._get import get  # noqa
except ImportError:
    raise
