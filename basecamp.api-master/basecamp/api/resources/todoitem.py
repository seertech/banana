"""Basecamp Todo Item

TodoItem schema:

<todo-item>
  <id type="integer">#{id}</id>
  <content>#{content}</content>
  <position type="integer">#{position}</position>
  <created-on type="datetime">#{created_on}</created-on>
  <creator-id type="integer">#{creator_id}</creator-id>
  <completed type="boolean">#{completed}</completed>

  <!-- if the item has a responsible party -->
  <responsible-party-type>#{responsible_party_type}</responsible-party-type>
  <responsible-party-id type="integer">#{responsible_party_id}</responsible-party-id>

  <!-- if the item has been completed -->
  <completed-on type="datetime">#{completed_on}</completed-on>
  <completer-id type="integer">#{completer_id}</completer-id>
</todo-item>

"""

from base import Resource
from attributes import StringAttribute, IntegerAttribute
from attributes import BooleanAttribute, DatetimeAttribute

class TodoItem(Resource):
    """Basecamp TodoItem class
    """
    
    _resource_type = 'todo-item'
    
    id = IntegerAttribute('id')
    content = StringAttribute('content')
    position = IntegerAttribute('position')
    created_on = DatetimeAttribute('created_on')
    creator_id = IntegerAttribute('creator_id')
    completed = BooleanAttribute('completed')
    responsible_party_type = StringAttribute('responsible_party_type')
    responsible_party_id = IntegerAttribute('responsible_party_id')
    completed_on = DatetimeAttribute('completed_on')
    completer_id = IntegerAttribute('completer_id')
