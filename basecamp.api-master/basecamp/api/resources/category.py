"""Basecamp Category

Category schema:

<category>
  <id type="integer">#{id}</id>
  <name>#{name}</name>
  <project-id type="integer">#{project_id}</project-id>
  <elements-count type="integer">#{elements_count}</elements-count>
  <type>#{type}</type>
</category>


"""

from base import Resource
from attributes import StringAttribute, IntegerAttribute

class Category(Resource):
    """Basecamp Category class
    """
    
    _resource_type = 'category'
    
    id = IntegerAttribute('id')
    name = StringAttribute('name')
    last_name = StringAttribute('last_name')
    project_id = IntegerAttribute('project_id')
    elements_count = IntegerAttribute('elements_count')
    type = StringAttribute('type')
