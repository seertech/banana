"""Basecamp Todo List

TodoList schema:

<todo-list>
  <id type="integer">#{id}</id>
  <name>#{name}</name>
  <description>#{description}</description>
  <project-id type="integer">#{project_id}</project-id>
  <milestone-id type="integer">#{milestone_id}</milestone-id>
  <position type="integer">#{position}</position>

  <!-- if user can see private lists -->
  <private type="boolean">#{private}</private>

  <!-- if the account supports time tracking -->
  <tracked type="boolean">#{tracked}</tracked>

  <!-- if todo-items are included in the response -->
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

from base import Resource
from todoitem import TodoItem
from attributes import StringAttribute, IntegerAttribute
from attributes import BooleanAttribute, ArrayAttribute

class TodoList(Resource):
    """Basecamp TodoList class
    """
    
    _resource_type = 'todo-list'
    
    id = IntegerAttribute('id')
    name = StringAttribute('name')
    description = StringAttribute('description')
    project_id = IntegerAttribute('project_id')
    milestone_id = IntegerAttribute('milestone_id')
    position = IntegerAttribute('position')
    private = BooleanAttribute('private')
    tracked = BooleanAttribute('tracked')
    todo_items = ArrayAttribute('todo_items', TodoItem)

