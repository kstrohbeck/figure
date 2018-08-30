class ConfigMeta(type):
    """Metaclass for configuration classes."""

    def __new__(mcs, name, bases, attrs):
        """Create a new config class.
        :param mcs: this metaclass
        :param name: the class name
        :param base: the classes inherited from
        :param attrs: dict of attributes
        :return: the config class
        """
        # TODO: How do we handle a class with _fields?
        attrs['_fields'] = []
        for key, val in attrs.iteritems():
            # TODO: Is there a better way to do this?
            if hasattr(val, '_figure_field'):
                val.attr_name = key
                attrs['_fields'].append(val)
        return super(ConfigMeta, mcs).__new__(mcs, name, bases, attrs)


class Config(object):
    """Base configuration class."""
    __metaclass__ = ConfigMeta

    def __init__(self):
        self._field_instances = [field.instance_for(self) for field in self._fields]
        for inst in self._field_instances:
            inst.initialize()

    def merge_source(self, source, prefix=None):
        if prefix is None:
            prefix = []
        for inst in self._field_instances:
            inst.load_from_source(source, prefix)

    def merge_sources(self, sources, prefix=None):
        for source in sources:
            self.merge_source(source, prefix)

    def validate(self):
        for inst in self._field_instances:
            inst.validate()
