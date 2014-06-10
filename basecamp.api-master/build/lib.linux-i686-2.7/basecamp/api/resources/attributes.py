"""Basecamp Resource Attributes

Resource &
Resource Attributes:
    string
    integer
    datetime
    object
    array
    boolean
    date
    
'nil'=true???

"""

import types

_marker = object()

class Attribute(object):
    """Base Attribute class
    """
    
    name = None
    value = None
    _valueType = None
    
    def __init__(self, name, value=_marker):
        self.name = name
        if value != _marker:
            self.value = value

    def getValue(self, instance):
        value = instance.__dict__.get(self.name, _marker)
        if value == _marker:
            return self.value
        return  value
    
    def setValue(self, instance, value):
        instance.__dict__[self.name] = value

    def hasValue(self, instance):
        return self.getValue(instance) is not None

    def __get__(self, instance, owner):
        if owner is None:
            return self
        return self.getValue(instance)
    
    def __set__(self, instance, value):
        self.setValue(instance, value)
    
    # XML related stuff    
    def serialize(self, instance):
        """Serialize attribute to xml format
        
        Supposed to be used only from extension class with set _valueType attribute.  
        """
        # skip attribute if it is None
        if not self.hasValue(instance):
            return ''
        return '<%(name)s type="%(type)s">%(value)s</%(name)s>' % {'name': self._xmlName(),
                                                                   'value': self._xmlValue(instance),
                                                                   'type': self._valueType}
    
    def _xmlName(self):
        """Serialize attribute name to suitable for xml format
        """
        return self.name.replace('_', '-')
    
    def _xmlValue(self, instance):
        """Serialize attribute value to suitable for xml format
        
        In extension classes this method should transform value to appropriate
        type before returning it for serialization.
        """
        return self.getValue(instance).encode('utf-8')


class StringAttribute(Attribute):
    """String Attribute
    
    e.g.
    <name>Basecamp API</name>
    """
    
    _valueType = 'string'
    
    def __set__(self, instance, value):
        """Ensure that attribute is string
        """
        self.setValue(instance, value)

    # XML related stuff    
    def serialize(self, instance):
        """Serialize attribute to xml format
        """
        if not self.hasValue(instance):
            return ''
        return '<%(name)s>%(value)s</%(name)s>' % {'name': self._xmlName(), 'value': self._xmlValue(instance)}
    
class IntegerAttribute(Attribute):
    """Integer Attribute
    
    e.g.
    <id type="integer">2572209</id>
    """
    
    _valueType = 'integer'
    
    def __set__(self, instance, value):
        """Ensure that attribute is integer
        """
        self.setValue(instance, int(value))

    # XML related stuff    
    def _xmlValue(self, instance):
        """Serialize attribute value to suitable for xml format
        """
        return str(int(self.getValue(instance)))

class DatetimeAttribute(Attribute):
    """Datetime Attribute
    
    e.g.
    <last-changed-on type="datetime">2008-10-26T15:36:52Z</last-changed-on>
    """
    
    _valueType = 'datetime'
    
    def __set__(self, instance, value):
        """Ensure that attribute is date/time
        """
        # TODO: transfrom into datetime format
        self.setValue(instance, value)
        
    # XML related stuff
    def _xmlValue(self, instance):
        """Serialize attribute value to suitable for xml date/time format
        """
        return self.getValue(instance).encode('utf-8')

class DateAttribute(Attribute):
    """Date Attribute
    
    e.g.
    <created-on type="date">2008-10-26</created-on>
    """
    
    _valueType = 'date'
    
    def __set__(self, instance, value):
        """Ensure that attribute is date
        """
        # TODO: transform into date format
        self.setValue(instance, value)
    
    # XML related stuff
    def _xmlValue(self, instance):
        """Serialize attribute value to suitable for xml date format
        """
        return self.getValue(instance).encode('utf-8')

class BooleanAttribute(Attribute):
    """Boolean Attribute
    
    e.g.
    <show-writeboards type="boolean">true</show-writeboards>
    <show-announcement type="boolean">false</show-announcement>
    """
    
    _valueType = 'boolean'
    
    def __set__(self, instance, value):
        """Ensure that attribute is boolean
        """
        if value and value != 'false':
            value = True
        else:
            value = False
        self.setValue(instance, value)
    
    # XML related stuff
    def _xmlValue(self, instance):
        """Serialize attribute value to suitable for xml format
        """
        if self.getValue(instance):
            return 'true'
        else:
            return 'false'

class ResourceAttribute(Attribute):
    """Resource Attribute
    
    Contains another REST Resource, e.g.
    <company>
      <id type="integer">1159235</id>
      <name>Company Name</name>
    </company>
    """
    
    _valueType = 'resource'
    
    def __init__(self, name, factory, value=_marker):
        super(ResourceAttribute, self).__init__(name, value)
        self.factory = factory

    def __set__(self, instance, value):
        """Ensure that attribute is resource of the given factory
        """
        if not isinstance(value, self.factory):
            # TODO: we should handle initialization arguments somehow
            value = self.factory.load(value)
        self.setValue(instance, value)

    # XML related stuff
    def serialize(self, instance):
        """Simply call serialize method of contained resource,
        if it is not empty
        """
        if not self.hasValue(instance):
            return ''
        return self.getValue(instance).serialize()

# TODO: inherit here from ListType...
class ArrayAttribute(Attribute):
    """Array Attribute
    
    Contains array of REST Resources of the same type, e.g.
    <todo-items type="array">
      <todo-item>
        ...
      </todo-item>
      <todo-item>
        ...
      </todo-item>
        ...
      </todo-items>
    </todo-list>
    """
    
    value = []
    _valueType = 'array'
    
    def __init__(self, name, factory, value=_marker):
        super(ArrayAttribute, self).__init__(name, value)
        self.factory = factory

    def __set__(self, instance, value):
        """Ensure that attribute is array of objects with the
        given factory type
        """
        # TODO: try not to deal with xml objects inside attributes on load
        if not isinstance(value, types.ListType):
            value = [self.factory.load(data) for data in value.childNodes if data.nodeType == data.ELEMENT_NODE]
        # Ensure that we holds only 'factory' types
        value = filter(lambda x: isinstance(x, self.factory), value)
        self.setValue(instance, value)

    # XML related stuff
    def serialize(self, instance):
        """Goes through array of resources and serializes them
        """
        xml = ''
        for resource in self.getValue(instance):
            if resource is None:
                continue
            xml += resource.serialize()
        return '<%(name)s>%(attrs)s</%(name)s>' % {'name': self._xmlName(), 'attrs': xml}

