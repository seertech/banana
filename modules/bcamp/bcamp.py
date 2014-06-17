from basecamp.api import Basecamp
import re
import time

class Bcamp:

	def run(self,input):
		method_checker = re.match('banana\s+basecamp\s+(\S*)',input)
		response = 'default'
		if(method_checker.group(1) == 'showlog'):
			""" syntax : banana basecamp showlog <username> <password> [starting date (yyyy-mm-dd)] [end date (yyyy-mm-dd)] """
			parser = re.match('banana\s+basecamp\s+showlog\s+(.+)\s+(.+)',input)

			if parser:
				print 'Please wait. Fetching logs.\n'
				response = self.show_logs(parser.group(1),parser.group(2))
				return response 

		else:
			response = 'Function not found!\n'

	def show_logs(self,username,password,starting='2000-01-01',ending=time.strftime("%Y-%m-%d")):
		bc = Basecamp('https://seertechnologies.basecamphq.com/',username,password)
		me = bc.getCurrentPerson().id
		total = 0.0

		projects = bc.getProjects()
		print projects[0]

		#bc.createTimeEntryForProject(projects[0],hours=hours,person_id=me,description=description)

		for te in bc.getEntriesReport(starting, ending, subject_id=me):
			print '%s: %0.2f' % (te.description, float(te.hours))

		return 'logs'
