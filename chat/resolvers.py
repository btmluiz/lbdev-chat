import abc

from channels.db import database_sync_to_async


class AbstractResolver(abc.ABC):

    def __init__(self, context=None):
        self.data = None
        self.context = context

    def set_data(self, data):
        self.data = data

    @abc.abstractmethod
    def resolve(self):
        pass


class ResolverError(Exception):
    pass


class SerializerResolver(AbstractResolver):
    def __init__(self, serializer, queryset, args=None, query_filter=None, query_exclude=None, query_get=None,
                 context=None):
        super().__init__(context=context)
        if args is None:
            args = {}
        self.serializer = serializer
        self.queryset = queryset
        self.filter = query_filter
        self.exclude = query_exclude
        self.get = query_get
        self.args = args

    def resolve_callables(self, target):
        if isinstance(target, dict):
            for x in target:
                if callable(target[x]):
                    target[x] = target[x](self.context, self.data)

    def resolve_all_callables(self):
        self.resolve_callables(self.filter)
        self.resolve_callables(self.exclude)
        self.resolve_callables(self.get)

    def apply_query_set(self):
        self.resolve_all_callables()
        if self.filter:
            self.queryset = self.queryset.filter(**self.filter)

        if self.exclude:
            self.queryset = self.queryset.exclude(**self.exclude)

        if self.get:
            self.queryset = self.queryset.get(**self.get)

        self.args["instance"] = self.queryset

    @database_sync_to_async
    def resolve(self):
        self.apply_query_set()
        serializer = self.serializer(**self.args, context=self.context)

        if "data" in self.args:
            if not serializer.is_valid():
                return serializer.errors
        return serializer.data


class MethodResolver(AbstractResolver):
    def __init__(self, method, context=None):
        super().__init__(context=context)
        self.method = method

    def resolve(self):
        return self.method(self.data)
