import logging

if not logging.root.handlers:
    logging.basicConfig(
        format="- %(levelname)4s %(message)s\n  from %(lineno)d:%(module)s"
    )
