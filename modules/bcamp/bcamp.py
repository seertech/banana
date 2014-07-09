import elementtree.ElementTree as ET
from basecamp import Basecamp
import ConfigParser
import re
import time
from datetime import datetime
import requests
import json
import redis

class Bcamp:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read("modules/bcamp/bcamp.cfg")
		self.api_token = config.get('Setup','apitoken')
		self.keyword = config.get('Setup','keyword')

	def cacheData(self):
		r = redis.StrictRedis(host='localhost',port=6379,db=0)
		bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
		i = 1
		userlist = {}

		xml = bc.people()
		items = ET.fromstring(xml).findall('person')
		for item in items:
			#all users in seer
			r.hset('Users:' + item.find('email-address').text, 'name',item.find('first-name').text + " " + item.find('last-name').text)
			r.hset('Users:' + item.find('email-address').text, 'id',item.find('id').text)
			r.hset('Users:' + item.find('email-address').text, 'email',item.find('email-address').text)

		xml = bc.projects()
		items = ET.fromstring(xml).findall('project')
		for item in items:
			#all projects under seer
			projectname = item.find('name').text
			projectid = item.find('id').text
			timekey = "time-" + projectid

			r.hset('Projects:' + projectname,"name",projectname)
			r.hset('Projects:' + projectname,"id",projectid)
			r.hset('Projects:' + projectname,"timekey","time-" + projectid)
			r.hset('Projects:' + projectname,"created-on",item.find('created-on').text)

			r.zadd('Projects',1,projectname)

			x = 1
			timeid = 1
			while 1:
				#every time log in a project
				time_entries = bc.time_entries_per_project(project_id = int(projectid), page = x)
				items2 = ET.fromstring(time_entries).findall('time-entry')
				count = 0
				for item2 in items2:

					todoitemid = item2.find('todo-item-id').text

					count = count + 1
					r.hset(timekey + ":" + str(timeid),'date',item2.find('date').text)
					r.hset(timekey + ":" + str(timeid),'hours',item2.find('hours').text)
					r.hset(timekey + ":" + str(timeid),'description',item2.find('description').text)
					r.hset(timekey + ":" + str(timeid),'personid',item2.find('person-id').text)
					r.hset(timekey + ":" + str(timeid),'todoitemid',item2.find('todo-item-id').text)

					r.zadd(timekey, int(item2.find('person-id').text),timeid)
					
					r.zadd("timeperuser-" + projectid, int(item2.find('person-id').text), timeid)

					timeid = timeid + 1

					print i
					i = i + 1

				if count != 50:
					break
				x = x + 1

			todolistkey = "todolist-" + projectid
			todolistid = 1

			todosearch = bc.todo_lists_per_project(project_id = int(projectid), filter = 'all')
			todo_lists = ET.fromstring(todosearch).findall('todo-list')
			for todo_list in todo_lists:
				#per todo list in a project
				listid = todo_list.find('id').text

				r.hset(todolistkey + ":" + str(todolistid),'name',todo_list.find('name').text)
				r.hset(todolistkey + ":" + str(todolistid),'id',todo_list.find('id').text)
				r.hset(todolistkey + ":" + str(todolistid),'completed',todo_list.find('completed').text)
				r.hset(todolistkey + ":" + str(todolistid),'todoitemkey',"todoitem-" + listid)

				todolistid = todolistid + 1

				todoitemkey = "todoitem-" + listid
				todoitemsearch = bc.items(list_id = int(listid))
				todo_items = ET.fromstring(todoitemsearch).findall('todo-item')

				todoitemid = 1

				for todo_item in todo_items:
					#per todo item in a todo list
					print 'todo item!!!'
					r.hset(todoitemkey + ":" + str(todoitemid),'content',todo_item.find('content').text)

					todoitemid = todoitemid + 1


			#messagekey = "message-" + projectid
			#messageid = 1

			#messagesearch = bc.messages_per_project(project_id = int(projectid))
			#messages = ET.fromstring(messagesearch).findall('post')
			#for message in messages:
				#per message in a project
				#r.hset(messagekey + ":" + str(messageid),'body',message.find('body').text)
				#r.hset(messagekey + ":" + str(messageid),'author-name',message.find('author-name').text)
				#r.hset(messagekey + ":" + str(messageid),'author-id',message.find('author-id').text)

				#messageid = messageid + 1

			#filekey = "file-" + projectid

			#filesearch = bc.attachments(project_id = int(projectid))
			#attachments = ET.fromstring(filesearch).findall('attachment')
			#for attachment in attachments:
				#per attachment in a project


		#for item in items:
			#projectname = item.find('name').text
			#projectid = item.find('id').text
			#timekey = "time-" + projectid

			#projectpeople = bc.people_per_project(int(item.find('id').text))
			#peoplesearch = ET.fromstring(projectpeople).findall('person')
			#for person in peoplesearch:
				#r.zadd("peopleperproject-" + projectid, int(person.find('id').text),person.find('email-address').text)



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
				project = r.hgetall(projectname)
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
				xml = bc.people()
				items = ET.fromstring(xml).findall('person')
				for item in items:
					if item.find('email-address').text == user_email:
						userid = item.find('id').text
						break
				
				if userid == '':
					response = 'Email not recognized!'
					return response

				projectpeople = bc.people_per_project(projectid)
				peoplesearch = ET.fromstring(projectpeople).findall('person')
				for person in peoplesearch:
					if int(person.find('id').text) == userid:
						bc.create_time_entry(desc,float(hour),int(userid),date,int(projectid),None)
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
				project = r.hgetall(projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response
				
				projectid = project['id']

				hour = parser.group(3)
				desc = parser.group(4)
				date = int(time.strftime("%Y%m%d"))

				getparams = {'token': 'xoxp-2315794369-2395812124-2401574040-f0d1b3','pretty':'1'}
				req = requests.get('https://slack.com/api/users.list', params=getparams)
				userlist = json.loads(req.content)
				user_email = ''
				for user in userlist['members']:
					if user['id'] == sender:
						user_email = user['profile']['email']

				userid = r.hget('Users',user_email)
				if userid == None or userid == '':
					response = 'Your email does not exist :<'
					return response

				checker = r.zrangebyscore("peopleperproject-" + projectid, userid, userid)
				if checker == None or checker == "" or checker == []:
					response = 'Your email is not recognized. Please try banana:: basecamp log <email> <"project name"> <hours> <"desc">'
					return response

				bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
				bc.create_time_entry(desc,float(hour),int(userid),date,int(projectid),None)
				
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
				userid = ''



				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				userid = r.hget('Users',email)

				print userid

				if userid == None or userid == "":
					response = 'Email not found!'
					return response

				projects = r.zrange('Projects',0,-1)
				for project in projects:
					projectid = r.hget(project,'id')
					projectname = r.hget(project,'name')
					checker = r.zrangebyscore("peopleperproject-" + projectid, userid, userid)
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
				userid = r.hget('Users',email)

				print userid

				if userid == None or userid == "":
					response = 'Email not found!'
					return response

				pname = r.hget(projectname,'name')
				if pname == "" or pname == None:
					response = 'Project not found'
					return response

				timekey = r.hget(projectname,'timekey')
				projectid = r.hget(projectname,'id')

				userposts = r.zrangebyscore(timekey,userid,userid)
				if userposts != None and userposts != "" and userposts != []:

					timeentries = r.zrangebyscore("timeperuser-" + projectid, userid, userid)
					for timeentry in timeentries:
						timedetails = r.hgetall(timekey + ":" + str(timeentry))
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
				userid = r.hget('Users',email)

				print userid

				if userid == None or userid == "":
					response = 'Email not found!'
					return response

				projects = r.zrange('Projects',0,-1)
				print projects


				for project in projects:
					timekey = r.hget(project,'timekey')
					projectid = r.hget(project,'id')
					projectname = r.hget(project,'name')

					userposts = r.zrangebyscore(timekey,userid,userid)
					if userposts != None and userposts != "" and userposts != []:

						instance = {'name':projectname,'hours':0,'percent':100}

						timeentries = r.zrangebyscore("timeperuser-" + projectid, userid, userid)
						for timeentry in timeentries:
							timedetails = r.hgetall(timekey + ":" + str(timeentry))
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

		#elif method_checker.group(2) == "get-logs":

		elif method_checker.group(2) == 'getTodoLists':
			""" banana: basecamp getTodoLists <"Project Name">"""
			regex = '(.*)\s%s\s+getTodoLists\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)

			response = ''

			if parser:
				projectname = parser.group(2)

				r = redis.StrictRedis(host='localhost',port=6379,db=0)
				project = r.hgetall(projectname)
				if project == None or project == [] or project == {}:
					response = 'Project not found'
					return response
					
				projectid = int(project['id'])
				todolistkey = "todolist-" + project['id']

				todolists = r.zrangebyscore(todolistkey,1,1)
				for todolist in todolists:
					print "todo-list"
					todolistdata = r.hgetall(todolistkey + ":" + todolist)
					response = response + todolistdata['name']

					todolistid = todolistdata['id']
					print todolistdata
					todoitemkey = todolistdata['todoitemkey']

					todoitems = r.zrange(todoitemkey,0,-1)
					for todoitem in todoitems:
						
						todoitemdata = r.hgetall(todoitemkey + ":" + todoitem)
						response = response + "    " + todoitemdata['content']

					response = response + "\n"



		else:
			response = 'Module not found!'

		return response
