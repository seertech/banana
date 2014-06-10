"""Base resource class

"""
import copy
from xml.dom import minidom

from attributes import Attribute

def tagName2Attribute(name):
    return name.replace('-', '_')

def attribute2TagName(name):
    return name.replace('_', '-')

class Resource(object):
    """Base class for Basecamp resources
    
    _resource_type - class attribute should have value equal to
                     xml tag name expressed by this resource
    """
    
    _resource_type = 'resource'

    def __init__(self, **kw):
        for name in self.fieldNames():
            if kw.has_key(name):
                setattr(self, name, kw[name])

    def fields(self):
        """Return all Attribute type fields
        """ 
        fields = []
        for name, attr in self.__class__.__dict__.items():
            if isinstance(attr, Attribute):
                fields.append((name, attr))
        return fields
    
    def fieldNames(self):
        """Return all Attribute type field names
        """
        return [field[0] for field in self.fields()]
    
    def __contains__(self, key):
        return key in self.fieldNames()
    
    # XML Layer
    def fromString(self, data):
        """Parse xml and return updated object
        """
        return self
    
    @classmethod
    def load(cls, data):
        """Goes through the given xml nodes and collect
        all needed data for Resource instantiation
        """
        resource = cls()
        for attr in data.childNodes:
            if attr.nodeType == attr.ELEMENT_NODE:
                if len(filter(lambda x: x.nodeType != attr.ELEMENT_NODE, attr.childNodes)) > 1:
                    # we found sub resource
                    value = attr
                elif len(filter(lambda x: x.nodeType != attr.ELEMENT_NODE, attr.childNodes)):
                    value = attr.childNodes[0].nodeValue
                elif attr.childNodes:
                    # only text child nodes
                    value = attr.nodeValue
                else:
                    #  or without children at all
                    continue
                setattr(resource, tagName2Attribute(attr.tagName), value)
        return resource
    
    def serialize(self):
        """Serialize to xml itself
        """
        xml = ''
        for name, field in self.fields():
            xml += field.serialize(self)
        return '<%(type)s>%(attrs)s</%(type)s>' % {'type': self._resource_type, 'attrs': xml}
    
    def prettyXML(self):
        """Serialize to pretty xml
        """
        return minidom.parseString(self.serialize()).toprettyxml()

    