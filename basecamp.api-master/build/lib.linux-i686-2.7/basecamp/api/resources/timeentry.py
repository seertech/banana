"""Basecamp Time Entry

TimeEntry schema:

<time-entry>
  <id type="integer">#{id}</id>
  <project-id type="integer">#{project-id}</project-id>
  <person-id type="integer">#{person-id}</person-id>
  <date type="date">#{date}</date>
  <hours>#{hours}</hours>
  <description>#{description}</description>
  <todo-item-id type="integer">#{todo-item-id}</todo-item-id>
</time-entry>

"""

from base import Resource
from attributes import StringAttribute, IntegerAttribute
from attributes import DateAttribute

class TimeEntry(Resource):
    """Basecamp TimeEntry class
    """
    
    _resource_type = 'time-entry'
    
    id = IntegerAttribute('id')
    project_id = IntegerAttribute('project_id')
    person_id = IntegerAttribute('person_id')
    date = DateAttribute('date')
    hours = StringAttribute('hours')
    description = StringAttribute('description')
    todo_item_id = IntegerAttribute('todo_item_id')
