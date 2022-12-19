import re
import typing as t
from inspect import signature, _empty as empty
from autoroutes import Routes
from collections import deque
from collections.abc import Hashable


def paths(path: str) -> t.Tuple[str, str]:
    stack = deque()
    path = path.strip('/')
    if not path:
        return stack
    steps = re.split(r'/+', path)
    nb = len(steps)
    while nb > 0:
        yield '/'.join(steps[0:nb]), '/'.join(steps[nb:])
        nb -= 1


C = t.TypeVar('C', bound=Hashable)
T = t.TypeVar('T', covariant=True)


class TypeMapping(t.Generic[T, C], t.Dict[t.Type[T], t.List[C]]):

    __slots__ = ()

    def add(self, cls: t.Type[T], component: C):
        components = self.setdefault(cls, [])
        components.append(component)

    @staticmethod
    def lineage(cls: t.Type[T]):
        yield from cls.__mro__

    def lookup(self, cls: t.Type[T]) -> t.Iterator[C]:
        for parent in self.lineage(cls):
            if parent in self:
                yield from self[parent]


class Node:

    def __init__(self, cls, url):
        self.cls = cls
        self.url = url

    def __hash__(self):
        return hash(self.cls)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.cls == other.cls and self.url == other.url
        return other == self.cls

    def __repr__(self):
        return f'{self.cls} -> {self.url}'


class Registry(t.Dict[t.Type, Routes]):

    __slots__ = ('_reverse')

    def __init__(self):
        self._reverse: TypeMapping[t.Any, t.Type] = TypeMapping()

    @staticmethod
    def lineage(cls):
        yield from cls.__mro__

    def lookup(self, cls) -> t.Optional[Routes]:
        for parent in self.lineage(cls):
            if parent in self:
                return self[parent]

    def add(self, root: t.Type[t.Any], path: str, factory: t.Callable):
        router = self.get(root)
        if router is None:
            router = self[root] = Routes()

        sig = signature(factory)
        if sig.return_annotation is empty:
            raise TypeError('Factories need to specify a return type.')
        self._reverse.add(sig.return_annotation, Node(root, path))
        router.add(path, factory=factory)

    def register(self, root: t.Type[t.Any], path: str):
        def factory_registration(factory):
            self.add(root, path, factory)
            return factory
        return factory_registration

    def resolve(
            self,
            root: t.Any,
            path: str,
            context: t.Optional[t.Mapping] = None) -> t.Any:

        matcher: Routes = self.lookup(root.__class__)
        for stub, branch in paths(path):
            found, params = matcher.match('/' + stub)
            if found:
                factory = found.get('factory')
                resolved = factory(root, context, **params)
                if not branch:
                    return resolved
                else:
                    return self.resolve(resolved, branch, context)
        raise LookupError()

    def reverse(self, node1, node2):
        path_list = [[node1]]
        path_index = 0

        # To keep track of previously visited nodes
        previous_nodes = {node1}
        if node1 == node2:
            return path_list[0]

        while path_index < len(path_list):
            current_path = path_list[path_index]
            last_node = current_path[-1]
            next_nodes = self._reverse[last_node]

            # Search goal node
            try:
                found = next_nodes.index(node2)
                current_path.append(next_nodes[found])
                return ''.join((node.url for node in reversed(current_path[1:])))
            except ValueError:
                pass

            # Add new paths
            for next_node in next_nodes:
                if not next_node in previous_nodes:
                    new_path = current_path[:]
                    new_path.append(next_node)
                    path_list.append(new_path)
                    # To avoid backtracking
                    previous_nodes.add(next_node)
            # Continue to next path in list
            path_index += 1
        # No path is found
        return []
