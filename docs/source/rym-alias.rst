`rym-alias`
==================================

The `alias` module provides name wranging functionality.

IMO, far too many software projects are fragile or backwards incompatible
due to trivial name changes, such as "prod", "PROD", or "production".
These name variations may be due to different developers or different
data sources -- it shouldn't matter.

We could setup some AI service with NLP, but that's silly. We want things
easier, not magic. We want to be explicit about the things we alias so
that our users do not have to be.

Usage
==================================

Create an Alias
----------------------------------

```python
>>> from rym.alias import Alias
>>> x = Alias('prd', aliases=['prod', 'production'])
>>> x.identify('prod')
'prd'
>>> x.identify('PROD')
'prd'
>>> x.identity
'prd'
>>> x.aliases
['prd', 'prod', 'production', 'PRD', 'PROD', 'PRODUCTION']
```

Specify Transformations
----------------------------------

Upper and lower case transformations are performed by default, but additional
transformations may be provided, too.

> Note: A `lambda` isn't needed in this example as `snakecase` matches the
> expected `Callable[[str], str]` signature already.

```python
>>> from rym.alias import Alias
>>> import stringcase as sc
>>> x = Alias('fooBar', transforms=[lambda x: sc.snakecase(x)])
>>> x.identify('fooBar')
'fooBar'
>>> x.identify('foo_bar')
'fooBar'
>>> x.aliases
['fooBar', 'foo_bar']
```

Use an Aliaser to Provide Multiple Aliases
----------------------------------

```python
>>> from rym.alias import Aliaser
>>> x = Aliaser.build(
...   prd=['prod'],
...   dev=['develop'],
... ).add(
...   alp=['alpha'],
...   transforms=[sc.titlecase],
... )
>>> x.identify('prod')
'prd'
>>> x.identify('develop')
'dev'
>>> x.identify('Alpha')
'alp'
>>> x.aliases
['prd', 'prod', 'dev', 'develop', 'PRD', 'PROD', 'DEV', 'DEVELOP', 'alp', 'alpha', 'Alp', 'Alpha']
```

You can specify transforms that apply to all aliases
And if you need to provide an alias to a keyword, just use a dictionary.

```python
>>> x.add({'transforms': 'etl'})
<class Aliaser>
>>> x.identify('etl')
'transforms'
```

API
==================================

.. automodule:: rym.lpath
    :members:
    :imported-members:

