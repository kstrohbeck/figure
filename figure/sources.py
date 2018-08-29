from __future__ import absolute_import, unicode_literals

import importlib
import os

try:
    import ConfigParser as configparser
except ImportError:
    import configparser


# Handle checking for strings on both Python 2 and 3.
try:
    basestring
except NameError:
    basestring = str


class Source(object):
    name = 'unknown source'

    def path_for(self, segments):
        return self.Path(self, segments)

    class Path(object):
        def __init__(self, source, segments):
            self.source = source
            self.segments = segments
            self._cache = {}

        @property
        def value(self):
            path_hash = tuple(self.segments)
            if path_hash not in self._cache:
                self._cache[path_hash] = self.get_value()
            return self._cache[path_hash]

        def __str__(self):
            return ''

        def get_value(self):
            raise NotImplementedError



class Environment(Source):
    name = 'environment'

    def __init__(self, prefix=None):
        self.prefix = prefix

    class Path(Source.Path):
        def __str__(self):
            segments = self.segments
            if self.source.prefix is not None:
                segments = [self.source.prefix] + segments
            return '_'.join(segments).upper()

        def get_value(self):
            return os.environ.get(str(self), None)


class FlatModule(Source):
    def __init__(self, module):
        if isinstance(module, basestring):
            try:
                module = importlib.import_module(module)
            except ImportError:
                module = None
        self.module = module

    @property
    def name(self):
        if self.module is not None:
            return self.module.__name__
        return 'unloaded module'

    class Path(Source.Path):
        def __str__(self):
            return '_'.join(self.segments).upper()

        def get_value(self):
            if self.source.module is not None:
                return getattr(self.source.module, str(self), None)


class Dict(Source):
    name = 'dict'

    def __init__(self, dct):
        self.dict = dct

    class Path(Source.Path):
        def __str__(self):
            return '.'.join(self.segments)

        def get_value(self):
            return _drill_down(self.source.dict, self.segments, lambda o, n: o.get(n, None))


class Object(Source):
    name = 'object'

    def __init__(self, obj):
        self.obj = obj

    class Path(Source.Path):
        def __str__(self):
            return '.'.join(self.segments)

        def get_value(self):
            return _drill_down(self.source.obj, self.segments, lambda o, n: getattr(o, n, None))


def _drill_down(obj, names, step):
    for name in names:
        obj = step(obj, name)
        if obj is None:
            return None
    return obj


class ConfigParser(Source):
    name = 'config parser'

    def __init__(self, parser, general='general', sep='.'):
        self.parser = parser
        self.general = general
        self.sep = sep

    class Path(Source.Path):
        @property
        def section(self):
            prefix = self.segments[:-1]
            if len(prefix) == 0:
                return self.source.general
            else:
                return self.source.sep.join(prefix)

        @property
        def option(self):
            return self.segments[-1]

        def __str__(self):
            return '[{}]{}'.format(self.section, self.option)

        def get_value(self):
            try:
                return self.source.parser.get(self.section, self.option)
            except (configparser.NoSectionError, configparser.NoOptionError):
                return None
