from flask.ext.mail import Message
from app import mail
from flask import render_template
from config import ADMINS
from threading import Thread
from app import app
from .decorators import async


@async
def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body # HTML messages throw an error with gmail smtp.
    send_async_email(app, msg)

# def send_email(subject, sender, recipients, text_body, html_body):
# 	'''
# 	Flask-Mail sends emails synchronously. The web server blocks while the email is being sent and only returns 
# 	its response back to the browser once the email has been delivered. Can you imagine what would happen if we 
# 	try to send an email to a server that is slow, or even worse, temporarily offline? Not good.
# 	'''
# 	msg = Message(subject, sender=sender, recipients=recipients)
# 	msg.body = text_body
# 	# msg.html = html_body # HTML messages throw an error with gmail smtp. With Yahoo, it only works if you comment out msg.body
# 	mail.send(msg)

def follower_notification(followed, follower):
	send_email("[microblog] %s is now following you!" % follower.nickname, ADMINS[0], [followed.email], 
		render_template("follower_email.txt", user=followed, follower=follower), 
		render_template("follower_email.html", user=followed, follower=follower))