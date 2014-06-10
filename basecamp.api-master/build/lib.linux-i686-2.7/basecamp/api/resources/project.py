"""Basecamp Project

Project schema:

<project>
  <id type="integer">#{id}</id>
  <name>#{name}</name>
  <created-on type="datetime">#{created_on}</created-on>
  <status>#{status}</status>
  <last-changed-on type="datetime">#{last_changed_on}</last-changed-on>
  <company>
    <id type="integer">#{id}</id>
    <name>#{name}</name>
  </company>

  <!-- if user is administrator, or show_announcement is true -->
  <announcement>#{announcement}</announcement>

  <!-- if user is administrator -->
  <start-page>#{start_page}</start-page>
  <show-writeboards type="boolean">#{show_writeboards}</show-writeboards>
  <show-announcement type="boolean">#{show_announcement}</show-announcement>
</project>


"""

from base import Resource
from company import Company
from attributes import StringAttribute, DatetimeAttribute, DateAttribute
from attributes import IntegerAttribute, BooleanAttribute, ResourceAttribute

class Project(Resource):
    """Basecamp Project class
    """
    
    _resource_type = 'project'
    
    id = IntegerAttribute('id')
    name = StringAttribute('name')
    created_on = DateAttribute('created_on')
    status = StringAttribute('status')
    last_changed_on = DatetimeAttribute('last_changed_on')
    company = ResourceAttribute('company', Company)
    announcement = StringAttribute('announcement')
    start_page = StringAttribute('start_page')
    show_writeboards = BooleanAttribute('show_writeboards')
    show_announcement = BooleanAttribute('show_announcement')
           
    
    