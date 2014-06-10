from basecamp.api import Basecamp

class Basecamp_module:

	def __init__(self):
		self.version = 1

	def show_logs(self,username='',password='',hours='',description=''):
		bc = Basecamp('https://seertechnologies.basecamphq.com','randall.castro@seer-technologies.com','asdasd123')
		me = bc.getCurrentPerson().id
		total = 0.0

		projects = bc.getProjects()
		print projects[0]

		#bc.createTimeEntryForProject(projects[0],hours=hours,person_id=me,description=description)

		for te in bc.getEntriesReport('2012-11-01', '2014-11-30', subject_id=me):
			print '%s: %0.2f' % (te.description, float(te.hours))
