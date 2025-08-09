class Component:
    """Base class for all components."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Entity:
    """Represents an entity with a collection of components."""

    def __init__(self):
        self.components = {}

    def add_component(self, component):
        """Add a component to the entity."""
        component_class = component.__class__
        self.components[component_class] = component

    def get_component(self, component_class):
        """Retrieve a component from the entity."""
        return self.components.get(component_class)


class System:
    """Base class for all systems."""

    def __init__(self):
        pass

    def update(self, entities):
        """Update function that processes entities."""
        raise NotImplementedError("Subclasses should implement this method.")


# Example components
class Position(Component):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)


class Velocity(Component):
    def __init__(self, dx, dy):
        super().__init__(dx=dx, dy=dy)


# Example system
class MovementSystem(System):
    """Example system that processes movement."""

    def __init__(self):
        super().__init__()

    def update(self, entities):
        for entity in entities:
            position = entity.get_component(Position)
            velocity = entity.get_component(Velocity)
            if position and velocity:
                position.x += velocity.dx
                position.y += velocity.dy
                print(f"Entity moved to ({position.x}, {position.y})")


# Example usage
if __name__ == "__main__":
    # Create entities
    entity1 = Entity()
    entity2 = Entity()

    # Add components to entities
    entity1.add_component(Position(x=0, y=0))
    entity1.add_component(Velocity(dx=1, dy=1))
    entity2.add_component(Position(x=10, y=5))
    entity2.add_component(Velocity(dx=-0.5, dy=0.5))

    # Create systems
    movement_system = MovementSystem()

    # Update systems
    entities = [entity1, entity2]
    movement_system.update(entities)
