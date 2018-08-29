"""Configuration fields."""
from __future__ import absolute_import, unicode_literals

import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """A problem with validation of a configuration object."""
    pass


class Field(object):
    """A field in a configuration object."""
    _figure_field = True

    def __init__(self, name=None, default=None):
        """Create a new field.
        :param name: the name of the field
        :param default: the field's default value
        """
        self.cfg = None
        self.attr_name = None
        self._name = name
        self.default = default

    @property
    def name(self):
        """The name of the field inside a source."""
        return self._name if self._name is not None else self.attr_name

    def instance_for(self, cfg):
        """Create an instance bound to a config.
        :param cfg: the cfg to bind to
        :return: an Instance
        """
        return self.Instance(self, cfg)

    class Instance(object):
        """An instance of a field bound to a config."""

        def __init__(self, field, cfg):
            """Create an instance of the field.
            :param field: the field this is an instance of
            :param cfg: the config to attach to
            """
            self.field = field
            self.cfg = cfg

        @property
        def attr(self):
            """The attribute on the config associated with the instance."""
            return getattr(self.cfg, self.field.attr_name)

        @attr.setter
        def attr(self, value):
            if value is not None:
                setattr(self.cfg, self.field.attr_name, value)

        def initialize(self):
            """Initialize the config attribute."""
            logger.info('Initializing %s to %s', self.field.attr_name, self.field.default)
            # If we use self.attr here, it won't set values where the default is None.
            setattr(self.cfg, self.field.attr_name, self.field.default)

        def get_path_segments(self, prefix):
            """Gets the list of path segments for this field.
            :param prefix: the segments prefixing this field
            :return: a list of segments
            """
            return prefix + [self.field.name]

        def get_from_source(self, source, prefix):
            """Get a value for this instance from a Source.
            :param source: the source to pull the value from
            :param prefix: the segments prefixing this field
            :return: the value, or None if it didn't exist
            """
            path = source.path_for(self.get_path_segments(prefix))
            if path.value is not None:
                logger.info('Got \'%s\' from %s as %s', path, source.name, path.value)
            else:
                logger.info('%s value doesn\'t exist for \'%s\'', source.name, path)
            return path.value

        def load_from_source(self, source, prefix):
            """Load this instance's attribute from a Source.
            :param source: the source to load the attribute from
            :param prefix: the segments prefixing this field
            """
            self.attr = self.get_from_source(source, prefix)

        def validate(self):
            """Validate that this attribute has been set by at least one Source."""
            if self.attr is None:
                raise ValidationError('Missing field \'{}\''.format(self.field.attr_name))


class String(Field):
    """A string valued field."""

    class Instance(Field.Instance):
        """An instance of the String field."""
        pass


class Int(Field):
    """An integral valued field."""

    class Instance(Field.Instance):
        """An instance of the Int field."""

        def load_from_source(self, source, path):
            value = self.get_from_source(source, path)
            if value is not None:
                self.attr = int(value)


class Nested(Field):
    """A field that maintains a nested configuration object."""

    def __init__(self, cls, **kwargs):
        Field.__init__(self, **kwargs)
        self.cls = cls

    class Instance(Field.Instance):
        """An instance of the Nested field."""

        def initialize(self):
            logger.info('Initializing \'%s\'', self.field.attr_name)
            self.attr = self.field.cls()

        def load_from_source(self, source, path):
            self.attr.merge_source(source, path + [self.field.name])

        def validate(self):
            self.attr.validate()
