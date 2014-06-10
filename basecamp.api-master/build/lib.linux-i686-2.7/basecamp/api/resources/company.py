"""Basecamp Company

Company schema:

<company>
  <id type="integer">#{id}</id>
  <name>#{name}</name>
  <address-one>#{address_one}</address-one>
  <address-two>#{address_two}</address-two>
  <city>#{city}</city>
  <state>#{state}</state>
  <zip>#{zip}</zip>
  <country>#{country}</country>
  <web-address>#{web_address}</web-address>
  <phone-number-office>#{phone_number_office></phone-number-office>
  <phone-number-fax>#{phone_number_fax}</phone-number-fax>
  <time-zone-id>#{time_zone_id}</time-zone-id>
  <can-see-private type="boolean">#{can_see_private}</can-see-private>

  <!-- for non-client companies -->
  <url-name>#{url_name}</url-name>
</company>


"""

from base import Resource
from attributes import StringAttribute, IntegerAttribute, BooleanAttribute

class Company(Resource):
    """Basecamp Company class
    """
    
    _resource_type = 'company'
    
    id = IntegerAttribute('id')
    name = StringAttribute('name')
    address_one = StringAttribute('address_one')
    address_two = StringAttribute('address_two')
    city = StringAttribute('city')
    state = StringAttribute('state')
    zip = StringAttribute('zip')
    country = StringAttribute('country')
    web_address = StringAttribute('web_address')
    phone_number_office = StringAttribute('phone_number_office')
    phone_number_fax = StringAttribute('phone_number_fax')
    time_zone_id = StringAttribute('time_zone_id')
    can_see_private = BooleanAttribute('can_see_private')
    url_name = StringAttribute('url_name')

    uuid = StringAttribute('uuid')
    
    