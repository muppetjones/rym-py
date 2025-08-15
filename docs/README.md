# Documentation

When adding a new package, follow these steps to update the docs:

1. Add path to `docs/Makefile`.
2. Add directory name to the namespaces list in `docs/source/conf.py`.
3. Add the package name to `docs/source/index.rst`.
4. Create `docs/source/{package-name}.rst`. See others for examples.
5. Add RST docstrings to modules defined under "Usage".
6. Add the package badge and links to the root README.
