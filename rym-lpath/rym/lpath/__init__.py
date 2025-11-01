# isort: skip_file

try:  # noqa
    from ._delim import (
        get_delimiter,
        get_default_delimiter,
        reset_delimiter,
        set_delimiter,
    )  # , _DELIMITER
    from ._get import get_value  # noqa
    from ._set import set_value  # noqa
    from ._remove import pop_value  # noqa

    # Aliases for compatibility and ease of use
    get = get_value
    set = set_value
    pop = pop_value
    remove = pop_value
except ImportError:
    raise
