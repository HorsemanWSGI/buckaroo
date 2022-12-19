import buckaroo


trail = buckaroo.Registry()


class Root:
    pass


class Model:

    def __init__(self, parent, id):
        self.parent = parent
        self.id = id

    def __repr__(self):
        return f'<Model {self.id} - {self.parent!r}>'


class SubModel(Model):

    def __repr__(self):
        return f'<SubModel {self.id} - {self.parent!r}>'


class Leaf:

    def __init__(self, parent, color):
        self.parent = parent
        self.color = color

    def __repr__(self):
        return f'<Leaf {self.color} - {self.parent!r}>'


@trail.register(Root, '/root/to/model/{id}')
def model_factory(parent, context, *, id):
    return Model(parent, id)


@trail.register(Root, '/root/to/submodel/{id}')
def submodel_factory(parent, context, *, id):
    return SubModel(parent, id)


@trail.register(Model, '/{color}')
def leaf_factory(parent, context, *, color):
    return Leaf(parent, color)


print(trail.resolve(Root(), '/root/to/model/123/red'))
print(trail.resolve(Root(), '/root/to/submodel/234/red'))

# LookupError
trail.resolve(Root(), '/root/to/nothing')
