import elementtree.ElementTree as ET
from basecamp import Basecamp
import ConfigParser
import re
import time
from datetime import datetime

class Bcamp:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read("modules/bcamp/bcamp.cfg")
		self.api_token = config.get('Setup','apitoken')
		self.keyword = config.get('Setup','keyword')

	def run(self,input,sender):
		regex = '(.*)\s%s\s+(\S*)' % self.keyword
		method_checker = re.match(regex,input)
		response = 'default'
		if(method_checker.group(2) == 'log'):
			""" banana:: basecamp log <"project name"> <hours> <"desc">"""
			regex = '(.*)\s%s\s+log\s+["|\'](.*)["|\']\s+([0-9]*[0-9]?\.+[0-9])\s+["|\'](.*)["|\']' % self.keyword
			parser = re.match(regex,input)
			
			if parser:

				projectname = parser.group(2)
				bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
				xml = bc.projects()
				items = ET.fromstring(xml).findall('project')
				for item in items:
					if item.find('name').text == projectname:
						projectid = item.find('id').text
						break

				print projectid
				hour = parser.group(3)
				desc = parser.group(4)
				date = int(time.strftime("%Y%m%d"))

				xml = bc.people()
				print xml
				bc.create_time_entry(desc,float(hour),11207005,date,int(projectid),None)
				#bc.create_time_entry("python",0.5,)
				response = 'Successfully logged!'

			else:
				response = 'Wrong set of parameters. Must be banana:: basecamp log <"project name"> <hours> <"description">'

		elif method_checker.group(2) == "getProjects":
			""" banana:: basecamp getProjects <email>"""
			regex = '(.*)\s%s\s+getProjects\s+(.*)' % self.keyword
			parser = re.match(regex,input)
			if parser:

				email = parser.group(2)
				projectlist = []
				userid = ''


				bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
				xml = bc.people()
				items = ET.fromstring(xml).findall('person')
				for item in items:
					if item.find('email-address').text == email:
						userid = item.find('id').text
						break

				xml = bc.projects()
				items = ET.fromstring(xml).findall('project')
				for item in items:
					projectpeople = bc.people_per_project(int(item.find('id').text))
					peoplesearch = ET.fromstring(projectpeople).findall('person')
					for person in peoplesearch:
						
						if person.find('id').text == userid:
							projectlist.append(item.find('name').text)
							break


				print projectlist
				response = "Projects of %s: \n\n" % email
				for project in projectlist:
					response = response + project + "\n"
				#bc.create_time_entry("python",0.5,)

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
				email = parser.group(3)
				date1 = parser.group(4)
				date1 = datetime(int(date1[0:4]), int(date1[5:7]), int(date1[8:10]))
				date2 = parser.group(5)
				date2 = datetime(int(date2[0:4]), int(date2[5:7]), int(date2[8:10]))
				user_time_entry = []

				bc = Basecamp('https://seertechnologies.basecamphq.com', self.api_token)
				xml = bc.projects()
				items = ET.fromstring(xml).findall('project')
				for item in items:
					if item.find('name').text == projectname:
						projectid = int(item.find('id').text)
						break

				print projectid

				xml = bc.people()
				items = ET.fromstring(xml).findall('person')
				for item in items:
					if item.find('email-address').text == email:
						userid = item.find('id').text
						break

				print userid

				x = 1
				time_entries = 'init'
				while 1:
					time_entries = bc.time_entries_per_project(project_id = projectid, page = x)
					items = ET.fromstring(time_entries).findall('time-entry')
					count = 0
					for item in items:
						count = count + 1
						if item.find('person-id').text == userid:
							
							entrydate = item.find('date').text
							entrydate = datetime(int(entrydate[0:4]), int(entrydate[5:7]), int(entrydate[8:10]))
							print 'match!'
							if entrydate >= date1 and entrydate <= date2:
								time_instance = []
								time_instance.append(item.find('date').text)
								time_instance.append(item.find('hours').text)
								time_instance.append(item.find('description').text)
								user_time_entry.append(time_instance)


					if count != 50:
						break
					x = x + 1

				print user_time_entry

				response = "Logs of %s: \n\n" % email
				for entry in user_time_entry:
					response = response + entry[0] + "   " + entry[1] + "   " + entry[2] + "\n"

			else:
				response = 'Wrong set of parameters. Must be banana:: basecamp getLogs <"project name"> <email> <yyyy-mm-dd> <yyyy-mm-dd>'

		else:
			response = 'Module not found!'

		return response