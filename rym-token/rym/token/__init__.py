# isort: skip_file
try:
    from .structures import Token, TokenSpec
    from .tokenizer import tokenize  # noqa
except ImportError:  # pragma: no cover
    raise
