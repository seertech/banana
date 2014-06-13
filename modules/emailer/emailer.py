import smtplib

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

	def printf(self):
		print "Hello World!"

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
		    print 'mail sent'
		except:
			print 'failed to send mail'