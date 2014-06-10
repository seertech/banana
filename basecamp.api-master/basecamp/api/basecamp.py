"""Basecamp API python wrapper

"""
import time
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from restclient import RESTClient
from restclient import absoluteURL
from resources import Project, Company, Person
from resources import Message, Category
from resources import TodoList, TodoItem, TimeEntry

# Basecamp errors
class UnauthorizedError(Exception):
    pass

class ForbiddenError(Exception):
    pass

class NotFoundError(Exception):
    pass


class Basecamp(object):
    """Python wrapper for Basecamp API
    """
    
    headers = {'Content-Type': 'application/xml',
               'Accept': 'application/xml'}
    
    def __init__(self, baseURL, username, password, headers={}):
        # normalize url
        url = absoluteURL(baseURL, '')
        if url.endswith('/'):
            url = url[:-1]
        self.url = url
        
        # set credentials
        self.username = username
        self.password = password
        self.requestHeaders = self.headers.copy()
        
        # instantiate and set REST client
        self.client = RESTClient()
        self.client.setCredentials(username, password)
        if isinstance(headers, dict):
            self.requestHeaders.update(headers)
        self.client.requestHeaders.update(self.requestHeaders)


    #
    # Basecamp API
    #
    
    
    # Projects API Calls
    
    def getProjects(self):
        """Get projects
                
        REST: GET /projects.xml
        
        Returns all accessible projects. This includes active, inactive, and archived projects.
        """
        path = '/projects.xml'
        rootElement = self.fromXML(self.get(path).contents)
        # TODO: use special Array attribute
        projects = []
        for data in rootElement.getElementsByTagName('project'):
            projects.append(Project.load(data))
        return projects

    def getProjectById(self, project_id):
        """Get project
        
        REST: GET /projects/#{project_id}.xml
        
        Returns a single project identified by its integer ID
        """
        # ensure that we got numerical project id
        assert isinstance(project_id, int)
        
        path = '/projects/%d.xml' % project_id
        response = self.get(path)
        if response.status == 404:
            raise NotFoundError, 'Project with %d id is not found!' % project_id
        
        rootElement = self.fromXML(response.contents)
        return Project.load(rootElement)


    # To-do Lists API Calls
    
    def getTodoLists(self, responsible_party=None, company=False):
        """Get all lists (across projects)
        
        REST: GET /todo_lists.xml?responsible_party=#{id}

        Returns a list of todo-list records, with todo-item records
        that are assigned to the given "responsible party". If no
        responsible party is given, the current user is assumed to
        be the responsible party. The responsible party may be changed
        by setting the "responsible_party" query parameter to a blank
        string (for unassigned items), a person-id, or a company-id
        prefixed by a "c" (e.g., c1234).
        """
        # make up a query string
        query = ''
        if responsible_party is not None:
            # ensure that we got numerical person or company id
            assert isinstance(responsible_party, int)
            
            query = '?responsible_party='
            if company:
                query += 'c'
            query += str(int(responsible_party))
        path = '/todo_lists.xml%s' % query
        response = self.get(path)
        if response.status == 404:
            if company:
                raise NotFoundError, 'Company with %d id is not found!' % responsible_party
            else:
                raise NotFoundError, 'Person with %d id is not found!' % responsible_party
            
        rootElement = self.fromXML(response.contents)
        # TODO: use special Array attribute
        todo_lists = []
        for data in rootElement.getElementsByTagName('todo-list'):
            todo_lists.append(TodoList.load(data))
        return todo_lists


    # To-do List Items API Calls

    def createTodoItem(self, todo_list_id, content, responsible_party=None,
                       company=False, notify=False):
        """Create todo item (for a given todo list)
        
        REST: POST /todo_lists/#{todo_list_id}/todo_items.xml
        
        Creates a new todo item record for the given list. The new record
        begins its life in the "uncompleted" state. (See the "Complete"
        and "Uncomplete" actions.) It is added at the bottom of the given 
        list. If a person is responsible for the item, give their id as the
        party_id value. If a company is responsible, prefix their company id
        with a 'c' and use that as the party_id value. If the item has a 
        person as the responsible party, you can also use the "notify" key to
        indicate whether an email should be sent to that person to tell them
        about the assignment.
        
        XML Request:
            <todo-item>
                <content>#{content}</content>

                <!-- if the item has a responsible party -->
                <responsible-party>#{party_id}</responsible-party>
                <notify type="boolean">#{true|false}</notify>
            </todo-item>
        
        Response:
            Returns HTTP status code 201 (Created) on success, with the
            Location header being set to the URL for the new item. (The new
            item's integer ID may be extractd from that URL.) 
        """
        # ensure that we got numerical todo list id
        assert isinstance(todo_list_id, int)
        if company and notify:
            raise Exception, 'You can not nofity company!'
        
        path = '/todo_lists/%d/todo_items.xml' % todo_list_id
        # find author
        author = ''
        if responsible_party is None:
            # add authenticated user
            person = self.getAuthenticatedPerson()
            if person is not None:
                responsible_party = person.id
        
        if responsible_party is not None:
            # ensure that we got numerical person or company id
            assert isinstance(responsible_party, int)
            
            author = '<responsible-party>%s%d</responsible-party>' % (
                company and 'c' or '',
                responsible_party
            )
        
        data = """
        <todo-item>
            <content>%s</content>
            %s
            <notify type="boolean">%s</notify>
        </todo-item>
        """ % (content,
               author,
               notify and 'true' or 'false')

        response = self.post(path, data=data)
        # successfuly created entry
        if response.status == 201:
            id = int(dict(response.headers)['location'].split('/')[-1])
            todo = TodoItem(id=id,
                            content=content,
                            responsible_party=responsible_party,
                            responsible_party_type=((company and
                                responsible_party) and 'c' or None),
                            creator_id=responsible_party)
            return todo
        return self.getErrors(response.contents)

    def completeTodoItem(self, todo_item_id):
        """Complete item
        
        REST: PUT /todo_items/#{id}/complete.xml

        Marks the specified todo item as completed.
        Response:
            Returns HTTP status code 200 on success.
        """
        # ensure that we got numerical id
        assert isinstance(todo_item_id, int)
    
        path = '/todo_items/%d/complete.xml' % todo_item_id
        response = self.put(path)
        
        # successfuly checked entry
        if response.status == 200:
            return True
        return self.getErrors(response.contents)

    def uncompleteTodoItem(self, todo_item_id):
        """Uncomplete item
        
        REST: PUT /todo_items/#{id}/uncomplete.xml

        If the specified todo item was previously marked as completed, this
        unmarks it, restoring it to an "uncompleted" state. If it was already
        in the uncompleted state, this call has no effect. 
        Response:
            Returns HTTP status code 200 on success.
        """
        # ensure that we got numerical id
        assert isinstance(todo_item_id, int)
    
        path = '/todo_items/%d/uncomplete.xml' % todo_item_id
        response = self.put(path)
        
        # successfuly checked entry
        if response.status == 200:
            return True
        return self.getErrors(response.contents)


    # Time Entries API Calls

    def getEntriesReport(self, _from, _to, subject_id=None, todo_item_id=None,
                         filter_project_id=None, filter_company_id=None):
        """Get time report

        REST: GET /time_entries/report.xml

        Returns the set of time entries that match the given criteria.

        This action accepts the following query parameters: from, to,
        subject_id, todo_item_id, filter_project_id, and filter_company_id. Both
        from and to should be dates in YYYYMMDD format, and can be used to
        restrict the result to a particular date range. (No more than 6 months'
        worth of entries may be returned in a single query, though). The
        subject_id parameter lets you constrain the result to a single person's
        time entries. todo_item_id restricts the result to only those entries
        relating to the given todo item. filter_project_id restricts the entries
        to those for the given project, and filter_company_id restricts the
        entries to those for the given company.

        Response:

            <time-entries type="array">
              <time-entry>
                ...
              </time-entry>
              ...
            </time-entries>
        """
        # ensure that we got numerical ids
        query = ['from=%s' % _from, 'to=%s' % _to]
        if subject_id:
            assert isinstance(subject_id, int)
            query.append('subject_id=%d' % subject_id)
        if todo_item_id:
            assert isinstance(todo_item_id, int)
            query.append('todo_item_id=%d' % todo_item_id)
        if filter_project_id:
            assert isinstance(filter_project_id, int)
            query.append('filter_project_id=%d' % filter_project_id)
        if filter_company_id:
            assert isinstance(filter_company_id, int)
            query.append('filter_company_id=%d' % filter_company_id)

        path = '/time_entries/report.xml?%s' % '&'.join(query)
        response = self.get(path)
        if response.status != 200:
            return self.getErrors(response.contents)

        rootElement = self.fromXML(response.contents)
        # TODO: use special Array attribute
        time_entries = []
        for data in rootElement.getElementsByTagName('time-entry'):
            time_entries.append(TimeEntry.load(data))
        return time_entries
    
    def getEntriesForTodoItem(self, todo_item_id):
        """Get all entries (for a todo item)
        
        REST: GET /todo_items/#{todo_item_id}/time_entries.xml
        
        Returns all time entries associated with the given todo item, in
        descending order by date. 
        
        Response:

            <time-entries type="array">
                <time-entry>
                    ...
                </time-entry>
                    ...
            </time-entries>
        """
        # ensure that we got numerical id
        assert isinstance(todo_item_id, int)
       
        path = '/todo_items/%d/time_entries.xml' % todo_item_id
        response = self.get(path)
        if response.status == 404:
            raise NotFoundError, 'Todo item with %d id is not found!' % \
                 todo_item_id
        
        rootElement = self.fromXML(response.contents)
        # TODO: use special Array attribute
        time_entries = []
        for data in rootElement.getElementsByTagName('time-entry'):
            time_entries.append(TimeEntry.load(data))
        return time_entries

    def createTimeEntryForTodoItem(self, todo_item_id, hours='', date=None,
                                   person_id=None, description=''): 
        """Create entry (for a todo item)
        
        REST: POST /todo_items/#{todo_item_id}/time_entries.xml
        
        Creates a new time entry for the given todo item.
        
        XML Request:
            <time-entry>
                <person-id>#{person-id}</person-id>
                <date>#{date}</date>
                <hours>#{hours}</hours>
                <description>#{description}</description>
            </time-entry>

        Response:
            Returns HTTP status code 201 (Created) on success, with the
            Location header set to the URL of the new time entry. The
            integer ID of the entry may be extracted from that URL.
        """
        # ensure that we got numerical todoitem id
        assert isinstance(todo_item_id, int)
        
        path = '/todo_items/%d/time_entries.xml' % todo_item_id
        # normalize all data for entry
        if date is None:
            # add current date
            date = time.strftime('%Y-%m-%d')
        # don't know how to get id of authenticated user
        if person_id is None:
            # add authenticated user
            person = self.getAuthenticatedPerson()
            if person is not None:
                person_id = person.id
        
        entry = TimeEntry(person_id=person_id,
                          todo_item_id=todo_item_id,
                          date=date,
                          hours=hours,
                          description=description)
        response = self.post(path, data=entry.serialize())
        
        # successfuly created entry
        if response.status == 201:
            entry.id = int(dict(response.headers)['location'].split('/')[-1])
            return entry
        return self.getErrors(response.contents)

    def createTimeEntryForProject(self, project_id, hours='', date=None,
                                  person_id=None, description=''):
        """Create entry (for a given project)
        
        REST: POST /projects/#{project_id}/time_entries.xml
        
        Creates a new time entry for the given todo item.
        
        XML Request:
            <time-entry>
                <person-id>#{person-id}</person-id>
                <date>#{date}</date>
                <hours>#{hours}</hours>
                <description>#{description}</description>
            </time-entry>

        Response:
            Returns HTTP status code 201 (Created) on success, with the
            Location header set to the URL of the new time entry. The
            integer ID of the entry may be extracted from that URL.
        """
        # ensure that we got numerical project id
        assert isinstance(project_id, int)
        
        path = '/projects/%d/time_entries.xml' % project_id
        # normalize all data for entry
        if date is None:
            # add current date
            date = time.strftime('%Y-%m-%d')
        # don't know how to get id of authenticated user
        if person_id is None:
            # add authenticated user
            person = self.getAuthenticatedPerson()
            if person is not None:
                person_id = person.id
        
        entry = TimeEntry(person_id=person_id,
                          project_id=project_id,
                          date=date,
                          hours=hours,
                          description=description)
        response = self.post(path, data=entry.serialize())
        
        # successfuly created entry
        if response.status == 201:
            entry.id = int(dict(response.headers)['location'].split('/')[-1])
            return entry
        return self.getErrors(response.contents)

    def destroyTimeEntry(self, id):
        """Destroy time entry
        
        REST: DELETE /time_entries/#{id}.xml

        Destroys the given time entry record.
        
        Response:
            Returns HTTP status code 200 on success.
        """
        # ensure we got numerical entry id
        assert isinstance(id, int)
        
        path = '/time_entries/%d.xml' % id
        response = self.delete(path)
        if response.status == 200:
            return True
        elif response.status == 404:
            raise NotFoundError, 'Time Entry with <%d> id is not found!' % id
        else:
            return self.getErrors(response.contents)


    # Companies API Calls
    
    def getCompanies(self):
        """Get companies
        
        REST: GET /companies.xml

        Returns a list of all companies visible to the requesting user.
        
        Response:
            <companies>
                <company>
                    ...
                </company>
                <company>
                    ...
                </company>
                ...
                </company>
            </companies>
        """
        path = '/companies.xml'
        rootElement = self.fromXML(self.get(path).contents)
        # TODO: use special Array attribute
        companies = []
        for data in rootElement.getElementsByTagName('company'):
            companies.append(Company.load(data))
        return companies
    
    def getCompaniesForProject(self, project_id):
        """Get companies on project
        
        REST: GET /projects/#{project_id}/companies.xml

        Returns a list of all companies associated with given project.
        
        Response:
            <companies>
                <company>
                    ...
                </company>
                <company>
                    ...
                </company>
                ...
                </company>
            </companies>
        """
        # ensure that we got numerical project id
        assert isinstance(project_id, int)
        
        path = '/projects/%d/companies.xml'
        response = self.get(path)
        if response.status == 404:
            raise NotFoundError, 'Project with %d id is not found!' % project_id
        
        rootElement = self.fromXML(response.contents)
        # TODO: use special Array attribute
        companies = []
        for data in rootElement.getElementsByTagName('company'):
            companies.append(Company.load(data))
        return companies
    
    def getCompanyById(self, company_id):
        """Get company
        
        REST: GET /companies/#{company_id}.xml

        Returns a single company identified by its integer ID.
        
        Response:
            <company>
                <id type="integer">1</id>
                <name>Globex Corporation</name>
            </company>
        """
        # ensure that we got numerical company id
        assert isinstance(company_id, int)
        
        path = '/companies/%d.xml' % company_id
        response = self.get(path)
        if response.status == 404:
            raise NotFoundError, 'Company with %d id is not found!' % company_id
        
        rootElement = self.fromXML(response.contents)
        return Company.load(rootElement)
        
    # People API Calls
    
    def getCurrentPerson(self):
        """Returns the currently logged in person (you)
        
        REST: GET /me.xml
        
        Response:

            <person>
              <id type="integer">#{id}</id>
              <user-name>#{user_name}</user-name>
              ...
            </person>
        """
        path = '/me.xml'
        response = self.get(path)
        if response.status != 200:
            return self.getErrors(response.contents)

        data = self.fromXML(response.contents)
        return Person.load(data)
    
    def getPeopleForCompany(self, company_id, project_id=None):
        """Get people (for company)
        
        REST: GET /contacts/people/#{company_id}

        This will return all of the people in the given company.
        If a project id is given, it will be used to filter the
        set of people that are returned to include only those
        that can access the given project.
        
        Response:
            <people>
                <person>
                    ...
                </person>
                <person>
                    ...
                </person>
                ...
            </people>
        """
        # ensure that we got numerical company id
        assert isinstance(company_id, int)
            
        path = '/contacts/people/%d' % company_id
        if project_id is not None:
            assert isinstance(project_id, int)
            path = '%s?project_id=%d' % (path, project_id)
        response = self.get(path)
        if response.status == 404:
            raise NotFoundError, 'Company [%d] or Project [%d] is not found!' % (company_id, project_id)
        
        rootElement = self.fromXML(response.contents)
        # TODO: use special Array attribute
        people = []
        for data in rootElement.getElementsByTagName('person'):
            people.append(Person.load(data))
        return people
    
    def getPeopleForProject(self, project_id, company_id):
        """Get people on project
        
        REST: GET /projects/#{project_id}/contacts/people/#{company_id}

        This will return all of the people in the given company that can
        access the given project.
        
        Response:
            <people>
                <person>
                    ...
                </person>
                <person>
                    ...
                </person>
                ...
            </people>
        """
        # ensure that we got numerical company and project ids
        assert isinstance(project_id, int)
        assert isinstance(company_id, int)
                    
        path = '/projects/%d/contacts/people/%d' % (project_id, company_id)
        response = self.get(path)
        if response.status == 404:
            raise NotFoundError, 'Project [%d] or Company [%d] is not found!' % (project_id, company_id)
        
        rootElement = self.fromXML(response.contents)
        # TODO: use special Array attribute
        people = []
        for data in rootElement.getElementsByTagName('person'):
            people.append(Person.load(data))
        return people
    
    def getPersonById(self, person_id):
        """Get person (by id)
        
        REST: GET /contacts/person/#{person_id}

        This will return information about the referenced person.
        
        Response:
            <person>
            ...
            </person>
        """
        # ensure that we got numerical person id
        assert isinstance(person_id, int)
        
        path = '/contacts/person/%d' % person_id
        response = self.get(path)
        if response.status == 404:
            raise NotFoundError, 'Person with %d id is not found!' % person_id
        
        rootElement = self.fromXML(response.contents)
        return Person.load(rootElement)
    
    def getPersonByLogin(self, login):
        """Finds person by it's login
        
        This method works only for persons from main company,
        not for persons from client companies.
        
        Return None if person wasn't found, and person if
        everything is fine.
        """
        # ensure that we got correct input
        assert isinstance(login, str)
        
        # get owner companies, can-see-private property should not be set
        companies = [company for company in self.getCompanies() if company.can_see_private is None]
        if len(companies):
            people = self.getPeopleForCompany(companies[0].id)
            for person in people:
                if person.user_name is not None and person.user_name.lower() == login.lower():
                    return person
        return None
    
    def getAuthenticatedPerson(self):
        """Get authenticated person
        
        Basecamp API doesn't provide any methods to get authenticated
        user. That's why this method is implemented using a few implicit
        calls to Basecamp API. This works not so quickly as it is
        supposed to, but at the moment it seems like the only way to
        accomplish this task.
        
        Thus, firstly we get all companies and find the owner company
        among them. Then fetch people for that company and finally loop
        through all the people to find the one where the username matches
        the current login. We take only the owner company because only
        persons from the owner company (not client company) are allowed
        to retrieve people for a company. This means that for others this
        approach won't work.
        
        So, in case we got:
            403 Error "The page you attempted to access is not accessible for clients",
        here is second way to get authenticated person.
        This approach is far from ideal. But as far as I know it is the only way
        to do this.
        
        Here are the detailed steps (http://www.basecamphq.com/forum-archive/viewtopic.php?id=2452):
            1.  Call /projects/list to get a list of projects.
            2.  Using the first project ID (it doesn't really matter which one it is),
                call /projects/#{project-id}/post_categories to get a category to post
                the message to.
            3.  Create a new message by calling /projects/#{project_id}/msg/create. (I use
                a GUID for the title of the message, but you could use anything you like.)
            4.  The reply you get back from /projects/#{project_id}/msg/create has two vital
                pieces of information.  The author-id node gives you your person ID (where
                "you" are the person whose credentials were used by the API to login).  The
                id node gives you the ID of the message, which you will use to ...
            5.  Call /msg/delete/#{id} using the message ID you just obtained.  This will
                delete the message you created.        
        """
        # first way for company owners
        try:
            person = self.getPersonByLogin(self.username)
        except (UnauthorizedError, ForbiddenError), e:
            # person doesn't belong to owner's company
            pass
        else:
            return person
        
        # second way for company clients
        projects = self.getProjects()
        if not len(projects) > 0:     # can't do anything if we have not projects yet
            return None
        
        # get categories in old way, cause new REST API won't allow us to
        # do this for client persons
        #categories = self.getCategories(projects[0].id, 'post')
        
        # TODO: this is not working either, ForbiddenError is raised
        rootElement = self.fromXML(self.get('/projects/%d/post_categories' % projects[0].id).contents)
        categories = rootElement.getElementsByTagName('post-category')
        if not len(categories) > 0:   # can't do anything if we have not categories yet
            return None
        else:
            category = Category.load(categories[0])
        
        # create message using legacy API, cause new REST based API
        # won't return any useful information in it's response
        path = '/projects/%d/msg/create' % projects[0].id
        message = Message(category_id=category.id,
                          title='temporary message to take login for client person')
        response = self.post(path, data="""<request>%s</request>""" % message.serialize())
        if response.status == 201:    # successfuly created entry
            message_id = int(dict(response.headers)['location'].split('/')[-1][:-4])
            self.destroyMessage(message_id)
            return message
        else:
            return None
    
    
    # Message API Calls
    
    def createMessage(self, project_id, title, category_id, body='',
                      extended_body='', private=0, notifiers=[],
                      attachments=[], milestone_id=None):
        """Create message
        
        REST: POST /projects/#{project_id}/posts.xml

        Creates a new message, optionally sending notifications
        to a selected list of people. Note that you can also upload
        files using this function, but you need to upload the files
        first and then attach them.
        
        XML Request:
            <request>
                <post>
                    <category-id>#{category_id}</category-id>
                    <title>#{title}</title>
                    <body>#{body}</body>
                    <extended-body>#{extended_body}</extended-body>
                    <private>1</private> <!-- only for firm employees -->
                </post>
                <notify>#{person_id}</notify>
                <notify>#{person_id}</notify>
                ...
                <attachments>
                    <name>#{name}</name> <!-- optional -->
                    <file>
                        <file>#{temp_id}</file> <!-- the id of the previously uploaded file -->
                        <content-type>#{content_type}</content-type>
                        <original_filename>#{original_filename}</original-filename>
                    </file>
                </attachments>
                <attachments>...</attachments>
                ...
            </request>

        Response:
            Returns HTTP status code 201 ("Created") on success, with the
            Location header set to the "Get message" URL for the new message.
            The new message ID can be extracted from that URL. On failure,
            a non-200 status code will be returned, possibly with error
            information in XML format as the response's content.
        """
        # ensure that we got correct input
        assert isinstance(project_id, int)
        assert isinstance(category_id, int)
        assert isinstance(title, str)
        if milestone_id is not None:
            assert isinstance(milestone_id, int)
        
        path = '/projects/%d/posts.xml' % project_id
        message = Message(category_id=category_id,
                          title=title,
                          project_id=project_id,
                          private=private,
                          body=body,
                          extended_body=extended_body)
        if milestone_id is not None:
            message.milestone_id = milestone_id
        
        notifiers = ''.join(['<notify>%d</notify>' % id for id in notifiers])
        attachments = ''.join([attachment.serialize() for attachments in attachments])
        body = """<request>%s%s%s</request>""" % (message.serialize(), notifiers, attachments)
                          
        response = self.post(path, data=body)

        # successfuly created entry
        if response.status == 201:
            message.id = int(dict(response.headers)['location'].split('/')[-1][:-4])
            return message
        return self.getErrors(response.contents)

    def destroyMessage(self, id):
        """Destroy message
        
        REST: DELETE /posts/#{id}.xml

        Destroys the given message and all of its associated comments.
        
        Response:
            Returns HTTP status code 200 on success.
        """
        # ensure we got numerical message id
        assert isinstance(id, int)
        
        path = '/posts/%d.xml' % id
        response = self.delete(path)
        if response.status == 200:
            return True
        elif response.status == 404:
            raise NotFoundError, 'Message with <%d> id is not found!' % id
        else:
            return self.getErrors(response.contents)
    
    
    # Categories API Calls
    
    def getCategories(self, project_id, cat_type=None):
        """Get categories
        
        REST: GET /projects/#{project_id}/categories.xml(?type=[post|attachment])

        Returns all categories for the given project. To filter by type, pass the
        type parameter, where type can be one of 'post' or 'attachment'.
        
        Response:
            <categories>
                <category>
                    <name>Documents</name>
                    ...
                </category>
                ...
            </categories>
        """
        # ensure we got valid input
        assert isinstance(project_id, int)
        
        path = '/projects/%d/categories.xml' % project_id
        if cat_type is not None:
            assert (isinstance(cat_type, str) and
                    cat_type.lower() in ['post', 'attachment'])
            path = '%s?type=%s' % (path, cat_type.lower())
            
        rootElement = self.fromXML(self.get(path).contents)
        # TODO: use special Array attribute
        categories = []
        for data in rootElement.getElementsByTagName('category'):
            categories.append(Category.load(data))
        return categories


    # Helpful functions
    
    def getErrors(self, xml):
        """Parse xml and return array of found errors"""
        errors = self.fromXML(xml)
        if errors is None:
            return ['Invalid xml in response: %s.' % xml]
        errors = errors.getElementsByTagName('error')
        return [error.childNodes[0].nodeValue for error in errors]
    
    def open(self, path='', data=None, params=None, headers={}, method='GET'):
        """Wrap RESTClient open method to add constantly some extra headers,
        catch a few common errors, etc...
        """
        url = '%s%s' % (self.url, path)
        
        # set Content-Length header in case it's not there already
        h = headers.copy()
        if not h.has_key('Content-Length'):
            h['Content-Length'] = isinstance(data, (str, unicode)) and len(data
                ) or 0
        
        self.client.open(url, data, params, h, method)
        if self.client.status == 401:
            raise UnauthorizedError, 'Perhaps your credentials (login or ' \
                'password) are not correct. %s (%s).' % (self.client.contents,
                url)
        elif self.client.status == 403:
            raise ForbiddenError, '%s (%s).' % (dict(self.client.headers
                )['status'], url)
        elif dict(self.client.headers)['status'] == \
             '404 The requested account could not be found':
            raise NotFoundError, 'The requested account could not be found. ' \
                '(%s)' % url
        return self.client
    
    def get(self, path='', params=None, headers={}):
        return self.open(path, None, params, headers)

    def put(self, path='', data='', params=None, headers={}):
        return self.open(path, data, params, headers, 'PUT')

    def post(self, path='', data='', params=None, headers={}):
        return self.open(path, data, params, headers, 'POST')

    def delete(self, path='', params=None, headers={}):
        return self.open(path, None, params, headers, 'DELETE')

    # Utility methods
    def fromXML(self, content):
        try:
            dom = minidom.parseString(content)
        except ExpatError, e:
            return None
        else:
            return dom.documentElement
