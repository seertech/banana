import elementtree.ElementTree as ET
from basecamp import Basecamp
import ConfigParser
import re
import time
from datetime import datetime
import requests
import json
import redis

from HTMLParser import HTMLParser
class MessageParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.output = ''

	def handle_starttag(self, tag, attrs):
		print "Encountered a start tag:", tag

	def handle_endtag(self, tag):
		print "Encountered an end tag :", tag

		if tag == 'br':
			self.output = self.output + '\n\n'

	def handle_data(self, data):
		print "Encountered some data  :", data

		self.output = self.output + ' ' + data


class Bcamp:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read("modules/bcamp/bcamp.cfg")
		self.api_token = config.get('Setup','apitoken')
		self.slack_token = config.get('Setup','slacktoken')
		self.keyword = config.get('Setup','keyword')

	def cacheData(self):
		r = redis.StrictRedis(host='localhost',port=6379,db=0)
		bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
		i = 1
		userlist = {}

		xml = bc.people().text
		items = ET.fromstring(xml).findall('person')
		for item in items:
			#all users in seer
			r.hset('Users:' + item.find('email-address').text, 'name',item.find('first-name').text + " " + item.find('last-name').text)
			r.hset('Users:' + item.find('email-address').text, 'id',item.find('id').text)
			r.hset('Users:' + item.find('email-address').text, 'email',item.find('email-address').text)

		xml = bc.projects().text
		items = ET.fromstring(xml).findall('project')
		for item in items:
			#all projects under seer
			projectname = item.find('name').text
			projectid = item.find('id').text
			print projectname
			print projectid

			r.hset('Projects:' + projectname,"name",projectname)
			r.hset('Projects:' + projectname,"id",projectid)

			r.zadd('Projects',1,projectname)

			x = 1
			while 1:
				#every time log in a project
				time_entries_data = bc.time_entries_per_project(project_id = int(projectid), page = x)

				if x > int(time_entries_data.headers['X-Pages']):
					break

				time_entries = time_entries_data.text

				items2 = ET.fromstring(time_entries).findall('time-entry')
				count = 0
				for item2 in items2:

					timeentryid = item2.find('id').text
					todoitemid = item2.find('todo-item-id').text

					count = count + 1
					r.hset('Time_entry:' + timeentryid,'date',item2.find('date').text)
					r.hset('Time_entry:' + timeentryid,'description', item2.find('description').text)
					r.hset('Time_entry:' + timeentryid,'hours',item2.find('hours').text)
					r.hset('Time_entry:' + timeentryid,'id',item2.find('id').text)
					r.hset('Time_entry:' + timeentryid,'person-id',item2.find('person-id').text)
					r.hset('Time_entry:' + timeentryid,'project-id',item2.find('project-id').text)
					r.hset('Time_entry:' + timeentryid,'todo-item-id',item2.find('todo-item-id').text)

					r.zadd('Time_entry:' + projectid, int(item2.find('person-id').text),timeentryid)

					print i
					i = i + 1

					print item2.find('description').text

				if count != 50:
					break

				x = x + 1

			todosearch = bc.todo_lists_per_project(project_id = int(projectid), filter = 'all').text
			todo_lists = ET.fromstring(todosearch).findall('todo-list')
			for todo_list in todo_lists:
				#per todo list in a project
				listid = todo_list.find('id').text

				r.hset("Todo_list:" + listid,'id',listid)
				r.hset("Todo_list:" + listid,'name',todo_list.find('name').text)
				r.hset("Todo_list:" + listid,'project-id',todo_list.find('project-id').text)
				r.hset("Todo_list:" + listid,'completed',todo_list.find('completed').text)
				r.hset("Todo_list:" + listid,'completed-count',todo_list.find('completed-count').text)
				r.hset("Todo_list:" + listid,'uncompleted-count',todo_list.find('uncompleted-count').text)
				r.hset("Todo_list:" + listid,'position',todo_list.find('position').text)

				r.zadd('Todo_list:' + projectid, 1, listid)

				todoitemsearch = bc.items(list_id = int(listid)).text
				todo_items = ET.fromstring(todoitemsearch).findall('todo-item')
				for todo_item in todo_items:
					#per todo item in a todo list
					itemid = todo_item.find('id').text

					r.hset("Todo_item:" + itemid,'id',itemid)
					r.hset("Todo_item:" + itemid,'content',todo_item.find('content').text)
					r.hset("Todo_item:" + itemid,'todo-list-id',todo_item.find('todo-list-id').text)

					r.zadd('Todo_item:' + listid, 1, itemid)

			messagesearch = bc.messages_per_project(project_id = int(projectid)).text
			messages = ET.fromstring(messagesearch).findall('post')
			for message in messages:
				#per message in a project
				postid = message.find('id').text

				r.hset("Message:" + postid,'id',postid)

				body = message.find('body').text

				#parser = MessageParser()
				#parser.feed(body)

				#parsed_message = parser.output
				parsed_message = body

				r.hset("Message:" + postid,'body',parsed_message)
				r.hset("Message:" + postid,'author-id',message.find('author-id').text)
				r.hset("Message:" + postid,'project-id',message.find('body').text)
				r.hset("Message:" + postid,'title',message.find('title').text)
				r.hset("Message:" + postid,'posted-on',message.find('posted-on').text)
				r.hset("Message:" + postid,'category-id',message.find('category-id').text)
				r.hset("Message:" + postid,'category-name',message.find('category-name').text)
				r.hset("Message:" + postid,'attachments-count',message.find('attachments-count').text)

				if int(message.find('attachments-count').text) > 0:
					attachments = message.findall('attachment')
					
					attachment_count = 1
					for attachment in attachments:
						r.hset("Attachment:" + postid + ":" + str(attachment_count),'id', attachment.find('id').text)
						r.hset("Attachment:" + postid + ":" + str(attachment_count),'download-url', attachment.find('download-url').text)
						r.hset("Attachment:" + postid + ":" + str(attachment_count),'project-id', attachment.find('project-id').text)
						r.hset("Attachment:" + postid + ":" + str(attachment_count),'person-id', attachment.find('person-id').text)
						r.hset("Attachment:" + postid + ":" + str(attachment_count),'name', attachment.find('name').text)
						attachment_count = attachment_count + 1

				r.zadd('Message:' + projectid, 1, postid)


			filesearch = bc.attachments(project_id = int(projectid)).text
			attachments = ET.fromstring(filesearch).findall('attachment')
			for attachment in attachments:
				#per attachment in a project
				attachmentid = attachment.find('id').text

				r.hset("Attachment:" + attachmentid,'id', attachment.find('id').text)
				r.hset("Attachment:" + attachmentid,'download-url', attachment.find('download-url').text)
				r.hset("Attachment:" + attachmentid,'project-id', attachment.find('project-id').text)
				r.hset("Attachment:" + attachmentid,'person-id', attachment.find('person-id').text)
				r.hset("Attachment:" + attachmentid,'name', attachment.find('name').text)


		for item in items:
			projectid = item.find('id').text

			projectpeople = bc.people_per_project(int(item.find('id').text)).text
			peoplesearch = ET.fromstring(projectpeople).findall('person')
			for person in peoplesearch:
				r.zadd("peopleperproject:" + projectid, int(person.find('id').text),person.find('email-address').text)



	def run(self,input,sender):
		regex = '(.*)\s%s\s+(\S*)' % self.keyword
		method_checker = re.match(regex,input)
		response = 'default'
		if(method_checker.group(2) == 'update'):
			""" banana: basecamp update"""
			self.cacheData()
			response = 'Updated!'

		elif(method_checker.group(2) == 'log'):
			""" banana:: basecamp log <email> <"project name"> <hours> <"desc">"""
			regex = '(.*)\s%s\s+log\s+(.*)\s+["|\'](.*)["|\']\s+([0-9]*[0-9]?\.+[0-9])\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)
			if parser:
				projectid = ''
				projectname = parser.group(3)

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				project = r.hgetall("Projects:" + projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response
				
				projectid = int(project['id'])

				hour = parser.group(4)
				desc = parser.group(5)
				date = int(time.strftime("%Y%m%d"))

				user_email = parser.group(2).split('|')[1][:-1]
				userid = ''

				bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
				xml = bc.people().text
				items = ET.fromstring(xml).findall('person')
				for item in items:
					if item.find('email-address').text == user_email:
						userid = item.find('id').text
						break
				
				if userid == '':
					response = 'Email not recognized!'
					return response

				projectpeople = bc.people_per_project(projectid).text
				peoplesearch = ET.fromstring(projectpeople).findall('person')
				for person in peoplesearch:
					if int(person.find('id').text) == userid:
						bc.create_time_entry(desc,float(hour),int(userid),date,int(projectid),None).text
						response = 'Logged successfully!'
						return response

				response = 'You do not belong to that project.'
				return response


			""" banana:: basecamp log <"project name"> <hours> <"desc">"""
			regex = '(.*)\s%s\s+log\s+["|\'](.*)["|\']\s+([0-9]*[0-9]?\.+[0-9])\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)
			
			if parser:
				print "log 2"
				projectid = ''
				projectname = parser.group(2)

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				project = r.hgetall("Projects:" + projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response
				
				projectid = project['id']

				hour = parser.group(3)
				desc = parser.group(4)
				date = int(time.strftime("%Y%m%d"))

				getparams = {'token': self.slack_token,'pretty':'1'}
				req = requests.get('https://slack.com/api/users.list', params=getparams)
				userlist = json.loads(req.content)
				user_email = ''
				for user in userlist['members']:
					if user['id'] == sender:
						user_email = user['profile']['email']

				userid = r.hget('Users:' + user_email,'id')
				if userid == None or userid == '':
					response = 'Your email does not exist :<'
					return response

				checker = r.zrangebyscore("peopleperproject:" + projectid, userid, userid)
				if checker == None or checker == "" or checker == []:
					response = 'Your email is not recognized. Please try banana:: basecamp log <email> <"project name"> <hours> <"desc">'
					return response

				bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
				bc.create_time_entry(desc,float(hour),int(userid),date,int(projectid),None).text
				
				return response

			else:
				response = 'Wrong set of parameters. Must be banana:: basecamp log <"project name"> <hours> <"description">'

		elif method_checker.group(2) == "getProjects":
			""" banana:: basecamp getProjects <email>"""
			regex = '(.*)\s%s\s+getProjects\s+(.*)' % self.keyword
			parser = re.match(regex,input)
			if parser:

				email = parser.group(2)
				email = email.split('|')[1][:-1]
				projectlist = []



				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				user = r.hgetall('Users:' + email)

				if user == None or user == "" or user == {}:
					response = 'Email not found!'
					return response

				userid = user['id']

				projects = r.zrange('Projects',0,-1)
				for project in projects:
					projectid = r.hget("Projects:" + project,'id')
					projectname = r.hget("Projects:" + project,'name')
					checker = r.zrangebyscore("peopleperproject:" + projectid, userid, userid)
					if checker != None and checker != "" and checker != []:
						projectlist.append(projectname)

				print projectlist
				response = "Projects of %s: \n\n" % email
				for project in projectlist:
					response = response + project + "\n"

			else:
				response = 'Wrong set of parameters. Must be banana:: basecamp getProjects <email>'

		elif method_checker.group(2) == "getLogs":
			""" banana:: basecamp getLogs <project name in quotation marks> <email> <yyyy-mm-dd> <yyyy-mm-dd>"""
			regex = '(.*)\s%s\s+getLogs\s+["|\'](.*)["|\']\s+(.*)\s+([0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9])\s+([0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9])' % self.keyword
			parser = re.match(regex,input)
			if parser:
				
				projectid = ''
				userid = ''
				projectname = parser.group(2)
				email = parser.group(3).split('|')[1][:-1]
				date1 = parser.group(4)
				date1 = datetime(int(date1[0:4]), int(date1[5:7]), int(date1[8:10]))
				date2 = parser.group(5)
				date2 = datetime(int(date2[0:4]), int(date2[5:7]), int(date2[8:10]))
				user_time_entry = []



				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				userid = r.hget('Users:' + email,'id')

				print userid

				if userid == None or userid == "":
					response = 'Email not found!'
					return response

				pname = r.hget('Projects:' + projectname,'name')
				if pname == "" or pname == None:
					response = 'Project not found'
					return response

				projectid = r.hget('Projects:' + projectname,'id')

				userposts = r.zrangebyscore('Time_entry:' + projectid,userid,userid)
				if userposts != None and userposts != "" and userposts != []:

					for userpost in userposts:
						timedetails = r.hgetall("Time_entry:" + str(userpost))
						entrydate = timedetails['date']
						entrydate = datetime(int(entrydate[0:4]), int(entrydate[5:7]), int(entrydate[8:10]))
						if entrydate >= date1 and entrydate <= date2:
							time_instance = []
							time_instance.append(timedetails['date'])
							time_instance.append(timedetails['hours'])
							time_instance.append(timedetails['description'])
							user_time_entry.append(time_instance)

				response = "Logs of %s: \n\n" % email
				for entry in user_time_entry:
					response = response + entry[0] + "   " + entry[1] + "   " + entry[2] + "\n"

			else:
				response = 'Wrong set of parameters. Must be banana:: basecamp getLogs <"project name"> <email> <yyyy-mm-dd> <yyyy-mm-dd>'


		elif method_checker.group(2) == "getDistribution":
			""" banana:: basecamp getDistribution <email>"""
			regex = '(.*)\s%s\s+getDistribution\s+(.*)' % self.keyword
			parser = re.match(regex,input)
			if parser:
				print 'getdist opening!!!'
				userid = ''
				email = parser.group(2).split('|')[1][:-1]
				"""distribution = [{'name':'example','hours':'69', 'percent':100}]"""
				distribution = []
				projectlist = []

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				userid = r.hget('Users:' + email,'id')

				print userid

				if userid == None or userid == "":
					response = 'Email not found!'
					return response

				projects = r.zrange('Projects',0,-1)
				print projects


				for project in projects:
					projectid = r.hget('Projects:' + project,'id')
					projectname = r.hget('Projects:' + project,'name')

					userposts = r.zrangebyscore("Time_entry:" + projectid,userid,userid)
					if userposts != None and userposts != "" and userposts != []:

						instance = {'name':projectname,'hours':0,'percent':100}

						for userpost in userposts:
							timedetails = r.hgetall("Time_entry:" + userpost)
							instance['hours'] = instance['hours'] + float(timedetails['hours'])

						distribution.append(instance)



				response = "Logs of %s: \n\n" % email
				total_hours = 0
				for entry in distribution:
					total_hours = total_hours + entry['hours']

				for entry in distribution:
					entry['percent'] = (float(entry['hours'])/float(total_hours)) * 100

				for entry in distribution:
					response = response + entry['name'] + "   " + str(entry['percent']) + "\n"

			else:
				response = 'Wrong set of parameters. Must be banana:: basecamp getDistribution <email>'

		elif method_checker.group(2) == "get-logs":
			""" banana: basecamp get-logs <"Project Name">"""
			regex = '(.*)\s%s\s+get[-]logs\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)

			response = ''

			if parser:
				projectname = parser.group(2)

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				project = r.hgetall("Projects:" + projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response

				projectid = project['id']

				people = r.zrange('peopleperproject:' + projectid, 0, -1)

				for user in people:
					userdata = r.hgetall('Users:' + user)
					response = response + userdata['name'] + '\n'

					time_entries = r.zrangebyscore("Time_entry:" + projectid, userdata['id'], userdata['id'])
					

					csvcontent = ''

					for time_entry in time_entries:
						time_entry_data = r.hgetall("Time_entry:" + time_entry)
						#response = response + '    ' + time_entry_data['description'] + '\n'

						csvcontent = csvcontent + time_entry_data['description'] + ',' + time_entry_data['hours'] + ',' + time_entry_data['date'] + ','

						#TO ADD LATER: Put these into seperate csv files

					postparams = {"content":csvcontent}
					getparams = {"token":self.slack_token,"channels":"C02BW6E2L", "filetype":"csv", "title":userdata['name'] + ' logs'}
					req = requests.post('https://slack.com/api/files.upload',params=getparams,data=postparams)

				response = 'Logs successfully saved in csv files!'


		elif method_checker.group(2) == 'getTodoLists':
			""" banana: basecamp getTodoLists <"Project Name">"""
			regex = '(.*)\s%s\s+getTodoLists\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)

			response = ''

			if parser:
				projectname = parser.group(2)

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				project = r.hgetall("Projects:" + projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response
					
				projectid = project['id']

				todolists = r.zrange("Todo_list:" + projectid,0,-1)
				for todolist in todolists:
					todolistdata = r.hgetall("Todo_list:" + todolist)
					response = response + todolistdata['name']

					todolistid = todolistdata['id']

					response = response + "\n"

		elif method_checker.group(2) == 'getMessages':
			""" banana: basecamp getMessages <"Project Name">"""
			regex = '(.*)\s%s\s+getMessages\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)

			response = ''

			if parser:
				projectname = parser.group(2)

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				project = r.hgetall("Projects:" + projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response
					
				projectid = project['id']

				messages = r.zrange("Message:" + projectid,0,-1)
				for message in messages:
					messagedata = r.hgetall("Message:" + message)
					response = response + messagedata['body'] + '\n'


					response = response + "\n"


		elif method_checker.group(2) == 'addTodoList':
			""" banana: basecamp addTodoList <"Project Name"> <"Todo List Name">"""
			regex = '(.*)\s%s\s+addTodoList\s+["|\'](.*)["|\']\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)

			response = ''

			if parser:
				projectname = parser.group(2)
				todolistname = parser.group(3)

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				project = r.hgetall("Projects:" + projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response
					
				projectid = project['id']

				bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
				bc.create_todo_list(project_id=int(projectid),name=todolistname)

				response = 'Todo List created successfully'


		elif method_checker.group(2) == 'addMessages':
			""" banana: basecamp addMessages <"Project Name"> <"">"""
			regex = '(.*)\s%s\s+addMessages\s+["|\'](.*)["|\']\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)

			response = ''

			#if parser:


		else:
			response = 'Module not found!'

		return response
