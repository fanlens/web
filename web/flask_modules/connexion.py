"""Supporting tools for connexion"""

import importlib

from connexion.operation import Operation
from connexion.resolver import Resolution, Resolver


def simple_resolve(operation: Operation) -> str:
    """
    Paths are translated into methods by joining the path with '_', removing '{}'s
    e.g. /hello/world:
            get
    will be resolved to
    hello_world_get()
    a plain / will be resolved to 'root'
    :param operation: the operation to resolve
    :return: operation converted to a string function name"""
    parts = []
    if operation.path == '/':
        parts.append('root')
    else:
        for part in operation.path.split('/'):
            if part:
                parts.append(part)
    parts.append(operation.method)
    func_name = '_'.join(parts).replace('{', '').replace('}', '')
    return func_name


class SimpleResolver(Resolver):
    """A custom `connexion` `Resolver` that works without relying on operation ids. See also `simple_resolve`"""

    def __init__(self, controller_module: object) -> None:
        """
        :param controller_module: the python module where the path implementations can be found
        """
        super().__init__(lambda _: _)  # we do it our own way, see resolve
        self._controller_module = controller_module

    def resolve(self, operation: Operation) -> Resolution:
        """
        :param operation: operation which will be resolved for this module
        :return: a resolved endpoint
        """
        func_name = simple_resolve(operation)
        func = getattr(self._controller_module, func_name)

        return Resolution(func, func_name)


class TaggedSimpleResolver(Resolver):
    """
    A custom `connexion` `Resolver` that works like `SimpleResolver` but looks for implementations in
    the `{controller_root}.{tag}` module instead of a single provided module. Untagged operations are looked up in
    `{controller_root}.default` by default.
    """

    def __init__(self, controller_root: object, default_tag: str = 'default') -> None:
        """
        :param controller_root: root for the controller modules
        :param default_tag: the tag to use if there is none specified
        """
        super().__init__(lambda _: _)  # we do it our own way, see resolve
        self._controller_root = controller_root
        self._default = [default_tag]

    def resolve(self, operation: Operation) -> Resolution:
        """
        :param operation: operation which will be resolved for this module
        :return: a resolved endpoint
        """
        func_name = simple_resolve(operation)

        tag: str
        tag, *_ = sorted(operation.operation.get('tags') or self._default)
        tag = tag.replace(' ', '_')

        # controller_module = getattr(self._controller_root, tag)
        # func = getattr(controller_module, func_name)
        controller_module = importlib.import_module(f'{self._controller_root.__name__}.{tag}')
        func = getattr(controller_module, func_name)

        return Resolution(func, func_name)
