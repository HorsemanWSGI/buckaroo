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
def model_factory(parent, context, *, id) -> Model:
    return Model(parent, id)


@trail.register(Root, '/root/to/submodel/{id}')
def submodel_factory(parent, context, *, id) -> SubModel:
    return SubModel(parent, id)


@trail.register(Root, '/root/submodel/{email}')
def submodel_factory_bis(parent, context, *, email) -> SubModel:
    return SubModel(parent, None)


@trail.register(Model, '/{color}')
def leaf_factory(parent, context, *, color) -> Leaf:
    return Leaf(parent, color)


import pdb
pdb.set_trace()
