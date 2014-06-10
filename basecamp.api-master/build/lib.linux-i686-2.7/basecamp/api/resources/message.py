"""Basecamp Message

Message schema:

<post>
  <id type="integer">#{id}</id>
  <title>#{title}</title>
  <body>#{body}</body>
  <posted-on type="datetime">#{posted_on}</posted-on>
  <project-id type="integer">#{project_id}</project-id>
  <category-id type="integer">#{category_id}</category-id>
  <author-id type="integer">#{author_id}</author-id>
  <milestone-id type="integer">#{milestone_id}</milestone-id>
  <comments-count type="integer">#{comments_count}</comments-count>
  <attachments-count type="integer">#{attachments_count}</attachments-count>
  <use-textile type="boolean">#{use_textile}</use-textile>
  <extended-body>#{extended_body}</extended-body>
  <display-body>#{display_body}</display-body>
  <display-extended-body>#{display_extended_body}</display-extended-body>

  <!-- if user can see private posts -->
  <private type="boolean">#{private}</private>
</post>


"""

from base import Resource
from attributes import StringAttribute, IntegerAttribute, DatetimeAttribute, BooleanAttribute

class Message(Resource):
    """Basecamp Message class
    """
    
    _resource_type = 'post'
    
    id = IntegerAttribute('id')
    title = StringAttribute('title')
    body = StringAttribute('body')
    posted_on = DatetimeAttribute('posted_on')
    project_id = IntegerAttribute('project_id')
    category_id = IntegerAttribute('category_id')
    author_id = IntegerAttribute('author_id')
    milestone_id = IntegerAttribute('milestone_id')
    comments_count = IntegerAttribute('comments_count')
    attachments_count = IntegerAttribute('attachments_count')
    use_textile = BooleanAttribute('use_textile')
    extended_body = StringAttribute('extended_body')
    display_body = StringAttribute('display_body')
    display_extended_body = StringAttribute('display_extended_body')
    private = BooleanAttribute('private')
