import re
import typing as t
from autoroutes import Routes
from collections import deque
from collections.abc import Hashable


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


def resolve(
        registry: TypeMapping,
        root: Any,
        path: str,
        context: t.Mapping) -> Any:

    matcher: Routes = registry.get(root.__class__)
    print(f'matcher for {root.__class__}')
    for stub, branch in paths(path):
        found: t.Optional[dict], params: t.Optional[dict] = matcher.match(
            '/' + stub
        )
        if found:
            factory = found.get('factory')
            resolved = factory(root, context, **params)
            if not branch:
                return resolved
            else:
                return resolve(registry, resolved, branch, context)
    raise LookupError()
