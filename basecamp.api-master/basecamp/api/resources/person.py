"""Basecamp Person

Person schema:

<person>
  <id type="integer">#{id}</id>
  <first-name>#{first_name}</first-name>
  <last-name>#{last_name}</last-name>
  <title>#{title}</title>
  <email-address>#{email_address}</email-address>
  <im-handle>#{im_handle}</im-handle>
  <im-service>#{im_service}</im-service>
  <phone-number-office>#{phone_number_office}</phone-number-office>
  <phone-number-office-ext>#{phone_number_office_ext}</phone-number-office-ext>
  <phone-number-mobile>#{phone_number_mobile}</phone-number-mobile>
  <phone-number-home>#{phone_number_home}</phone-number-home>
  <phone-number-fax>#{phone_number_fax}</phone-number-fax>
  <last-login type="datetime">#{last_login}</last-login>
  <client-id type="integer">#{client_id}</client-id>

  <!-- if user is an administrator, or is self -->
  <user-name>#{user_name}</user-name>

  <!-- if user is self -->
  <password>#{password}</password>
  <token>#{token}</token>

  <!-- if user is an administrator -->
  <administrator type="boolean">#{administrator}</administrator>
  <deleted type="boolean">#{deleted}</deleted>
  <has-access-to-new-projects type="boolean">#{has_access_to_new_projects}</has-access-to-new-projects>
</person>

"""

from base import Resource
from attributes import StringAttribute, IntegerAttribute, DatetimeAttribute, BooleanAttribute

class Person(Resource):
    """Basecamp Person class
    """
    
    _resource_type = 'person'
    
    id = IntegerAttribute('id')
    first_name = StringAttribute('first_name')
    last_name = StringAttribute('last_name')
    title = StringAttribute('title')
    email_address = StringAttribute('email_address')
    im_handle = StringAttribute('im_handle')
    im_service = StringAttribute('im_service')
    phone_number_office = StringAttribute('phone_number_office')
    phone_number_office_ext = StringAttribute('phone_number_office_ext')
    phone_number_mobile = StringAttribute('phone_number_mobile')
    phone_number_home = StringAttribute('phone_number_home')
    phone_number_fax = StringAttribute('phone_number_fax')
    last_login = DatetimeAttribute('last_login')
    client_id = IntegerAttribute('client_id')
    user_name = StringAttribute('user_name')
    password = StringAttribute('password')
    token = StringAttribute('token')
    administrator = BooleanAttribute('administrator')
    deleted = BooleanAttribute('deleted')
    has_access_to_new_projects = BooleanAttribute('has_access_to_new_projects')
