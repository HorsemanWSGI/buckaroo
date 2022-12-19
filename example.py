import buckaroo


trail = buckaroo.Registry()


class Root:
    pass


class Model:

    def __init__(self, parent, id):
        self.parent = parent
        self.id = id

    def __repr__(self):
        return f'<Model {self.id} - {self.parent!r}'


class Leaf:

    def __init__(self, parent, color):
        self.parent = parent
        self.color = color

    def __repr__(self):
        return f'<Leaf {self.color} - {self.parent!r}'


@trail.register(Root, '/root/to/model/{id}')
def model_factory(parent, context, *, id):
    return Model(parent, id)


@trail.register(Model, '/{color}')
def leaf_factory(parent, context, *, color):
    return Leaf(parent, color)


print(trail.resolve(Root(), '/root/to/model/123/red', context={}))


# LookupError
trail.resolve(Root(), '/root/to/nothing', context={})
