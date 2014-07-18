import ConfigParser
import re
import requests
import datetime
import json
import codecs

class Slack:
	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read("modules/slack/slack.cfg")
		self.slack_token = config.get('Setup','slacktoken')
		self.keyword = config.get('Setup','keyword')

	def archive(self):
		getparams = {'token': self.slack_token}
		req = requests.get('https://slack.com/api/users.list', params=getparams)
		memberlist = json.loads(req.content)

		members = {}

		for member in memberlist['members']:
			members[member['id']] = member['name']



		getparams = {'token': self.slack_token}
		req = requests.get('https://slack.com/api/channels.list', params=getparams)
		channellist = json.loads(req.content)

		path = "archive/"

		for channel in channellist['channels']:
			channelid = channel['id']
			channelname = channel['name']
			print channelname
			oldest = 0
			f = ''

			try: 
				with open(path + channelname + '-ch.log','r') as f:
					data = f.readlines()

					checker = len(data) - 1

					while 1:
						oldest = data[checker][0:17]
						regex = '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][.][0-9][0-9][0-9][0-9][0-9][0-9]'
						ts_check = re.match(regex,oldest)
						if(ts_check):
							break
						checker = checker - 1
				
			except IOError:
				oldest = 0
				with open(path + channelname + '-ch.log','w') as f:
					f.write(channelid + ' ' + channelname + '\n')


			getparams = {'token': self.slack_token,'channel':channelid, 'latest':oldest, 'count':1000}
			req = requests.get('https://slack.com/api/channels.history', params=getparams)
			channelhistory = json.loads(req.content)

			for message in channelhistory['messages']:
				f = codecs.open(path + channelname + '-ch.log','a','utf8')
					#Append timestamp - date(mm-dd-yyyy) - sender - message

				if 'subtype' in message:
					if message['subtype'] == 'message_changed':
						f.write(message['ts'] + '   ' + datetime.datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S') + '   ' + members[message['message']['user']] + '  :  ' + message['message']['text'] + '\n')
						#print message['message']['text'].encode('utf8')
						continue

					elif message['subtype'] == 'file_comment':
						f.write(message['ts'] + '   ' + datetime.datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S') + '   ' + members[message['comment']['user']] + '  :  ' + message['comment']['comment'] + '\n')
						#print message['message']['text'].encode('utf8')
						continue

					elif message['subtype'] == 'file_share' and message['upload'] == False:
						continue

					elif message['subtype'] == 'message_deleted' or message['subtype'] == 'bot_message' or message['subtype'] == 'bot_message':
						continue

				f.write(message['ts'] + '   ' + datetime.datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S') + '   ' + members[message['user']] + '  :  ' + message['text'] + '\n')
				#print message['text'].encode('utf8')

			f.close()


		getparams = {'token': self.slack_token}
		req = requests.get('https://slack.com/api/groups.list', params=getparams)
		grouplist = json.loads(req.content)

		for group in grouplist['groups']:
			groupid = group['id']
			groupname = group['name']
			oldest = 0
			f = ''

			try: 
				with open(path + groupname + '-pg.log','r') as f:
					data = f.readlines()

					checker = len(data) - 1

					while 1:
						oldest = data[checker][0:17]
						regex = '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][.][0-9][0-9][0-9][0-9][0-9][0-9]'
						ts_check = re.match(regex,oldest)
						if(ts_check):
							break
						checker = checker - 1
				
			except IOError:
				oldest = 0
				with open(path + groupname + '-pg.log','w') as f:
					f.write(groupid + ' ' + groupname + '\n')


			getparams = {'token': self.slack_token,'channel':groupid, 'latest':oldest, 'count':1000}
			req = requests.get('https://slack.com/api/groups.history', params=getparams)
			grouphistory = json.loads(req.content)

			for message in grouphistory['messages']:
				f = codecs.open(path + groupname + '-pg.log','a','utf8')
					#Append timestamp - date(mm-dd-yyyy) - sender - message

				if 'subtype' in message:
					if message['subtype'] == 'message_changed':
						f.write(message['ts'] + '   ' + datetime.datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S') + '   ' + members[message['message']['user']] + '  :  ' + message['message']['text'] + '\n')
						#print message['message']['text'].encode('utf8')
						continue

					elif message['subtype'] == 'file_comment':
						f.write(message['ts'] + '   ' + datetime.datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S') + '   ' + members[message['comment']['user']] + '  :  ' + message['comment']['comment'] + '\n')
						#print message['message']['text'].encode('utf8')
						continue

					elif message['subtype'] == 'file_share' and message['upload'] == False:
						continue

					elif message['subtype'] == 'message_deleted' or message['subtype'] == 'bot_message' or message['subtype'] == 'bot_message':
						continue

				f.write(message['ts'] + '   ' + datetime.datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S') + '   ' + members[message['user']] + '  :  ' + message['text'] + '\n')
				#print message['text'].encode('utf8')

			f.close()







	def run(self,input,sender):
		regex = '(.*)\s%s\s+(\S*)' % self.keyword
		method_checker = re.match(regex,input)
		response = 'default'
		if(method_checker.group(2) == 'archive'):
			""" banana:: slack archive"""
			self.archive()
			response = 'Slack Archived!'

		return response