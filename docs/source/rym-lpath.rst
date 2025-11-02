`rym-lpath`
==================================

The `lpath` module serves two primary purposes:

1. Easier access for nested structures
2. Consistent interface regardless of access type

It's a simple enough premise, and possibly over-engineered, but `lpath` can help
lower code redundancy and complexity by reducing the number of try-except blocks
and specialized handling needed for nested structures.

The primary use is `lpath.get`. With `get`, you don't really need anything else
as you can add, remove, and update once you've pulled the appropriate item.

CHANGELOG
----------------------------------

v1.0.0
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Consolidated most lpath errors into one of two types:
    - `InvalidKeyError(KeyError)`: Raised for any attribute, key, or index
        lookup error.
    - `KeyFormatError(ValueError)`: Raised when the key cannot be processed.
        - [BREAKING] This error can no longer trigger 'default' behavior.
- ExceptionGroups can be enabled for fine-tuned error handling with `except*`

    ```python
    from rym import lpath
    lpath.enable_exception_groups()
    ```

- Renamed core functions to `*_value` to prevent namespace pollution. There is
    no impact to code using the module directly, e.g., `lpath.set`.
    - [BREAKING] If imported directly from the modules, imports will need to be
        updated, e.g., `from rym.lpath._set import set_value`

Usage
----------------------------------

.. automodule:: rym.lpath._get

.. automodule:: rym.lpath._set

.. automodule:: rym.lpath._remove

.. automodule:: rym.lpath.errors


API
----------------------------------

.. automodule:: rym.lpath
    :members:
    :imported-members:

