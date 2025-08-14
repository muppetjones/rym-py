# Registrar

One of the big benefits of ECS is composition over inheritance: Entities are little
more than identifiers associated with one or more components. This pattern requires
efficient lookup by component:

1. Must lookup entities by one or more component types.
2. Must match against entities based on component values.

The second requirement implies support for expression evaluation, e.g.,
`Health.percentage < 100` would return all entities with matching health components.
This requirement will not be implemented initially.

The first requirement suggests the following features:

1. Index of components by type
2. Index of components by entity
3. Reference to entity on each component

Rather than building a separate registrar for each index, we can use a single registrar
with multiple indices on a single register that stores both components and entities
by a unique identifier (UID). In a future state, we'll very likely need a separate
register for components and entities, but a single register should work for now.

The register will be a dictionary to support the UID lookup. A list- or deque-based
implementation could be more efficient, but integer lookup is a little more fragile
than a UID lookup, and it would also need a way to handle removal and addition of
items more cleanly, which I don't want to mess with right now -- it's trivial, but
it's more effort with minimal benefit for a side project. However, dictionary
performance decreases with too many items -- cross that bridge when we get there.

For simplicity, component IDs will also be stored on an entity object instead of
in a separate index.
