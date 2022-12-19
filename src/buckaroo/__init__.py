import re
import typing as t
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


class TypeMapping(t.Generic[T, C], t.Dict[t.Type[T], C]):

    __slots__ = ()

    @staticmethod
    def lineage(cls: t.Type[T]):
        yield from cls.__mro__

    def lookup(self, cls: t.Type[T]) -> C:
        for parent in self.lineage(cls):
            if parent in self:
                return self[parent]


class Registry(TypeMapping[t.Any, Routes]):

    def add(self, root: t.Type[t.Any], path: str, factory: t.Callable):
        router = self.get(root)
        if router is None:
            router = self[root] = Routes()
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
