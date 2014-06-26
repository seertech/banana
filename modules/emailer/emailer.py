import smtplib
import re
import redis

class Emailer:

	"""
	Function description : 
		sends an email given certain details patterned from http://stackoverflow.com/questions/10147455/trying-to-send-email-gmail-as-mail-provider-using-python
	Parameters:
		details -> a dictionary that contains user info and email ifo
		attributes:
			sender -> the email address that will send the email
			recipients -> a list of email addresses that the email will be sent to
			subject -> subject of the email
			text -> the content of the message body
			username -> the username of the account that will send the email
			password -> the password of the account that will send the email
	"""
	def send_email(self,details):

		msg = """ \From: %s\nTo: %s\nSubject: %s\n\n%s
		""" % (details['sender'],", ".join(details['recipients']),details['subject'],details['text'])

		try:
			#initialize an email server at gmail using smtp protocol
		    server = smtplib.SMTP('smtp.gmail.com:587')
		    server.ehlo()
		    #put the smtp server in transport layer security mode
		    server.starttls()
		    #login to the email account using email-password combination
		    server.login(details['username'],details['password'])
		    #send the email
		    server.sendmail(details['sender'],details['recipients'],msg)
		    #server.quit()
		    server.close()
		    return 'mail sent'
		except smtplib.SMTPAuthenticationError:
			return 'invalid username-password combination'

		except:
			return 'failed to send mail'
	def run(self,input):
		r = redis.StrictRedis(host='localhost',port=6379,db=0)
		method_checker = re.match(r'banana\s+emailer\s+(\S*)',input)
		response = 'default'
		if(method_checker.group(1) == 'send'):
			""" syntax : banana emailer send <sending email> <receiving email/s> <subject in quotes> <body in quotes> <password in quotes> """
			parser = re.match(r'banana\s+emailer\s+send\s+([^@]+@[^@]+\.[^@]+)\s+([^@]+@[^@]+\.[^@]+)\s+"(.*)"\s+"(.*)"\s+"(.*)"',input)
			
			if parser:
				
				receiving = parser.group(2).split(',')
				details = {'sender' : parser.group(1),'recipients' : receiving,'subject' : parser.group(3),'text' : parser.group(4),'username' : parser.group(1),'password' : parser.group(5)}
				print 'Please wait. Sending email.\n'
				response = self.send_email(details)
				return response

			else:
				response = 'Wrong set of Parameters!\n'

		else:
			response = 'Function not found!\n'

		return response