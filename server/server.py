
# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
import json


# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'AC86e5b9f023f7fb9ce3d6d6a89ac48cf1'
auth_token = '4392a5cd91044ef37a781f01a2289074'
client = Client(account_sid, auth_token)

safety = True

def send_message(text):
	message = client.messages \
                .create(
                     body=text,
                     from_='+18556426431',
                     to='+12066696224'
                 )


app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():
    """Respond to incoming messages with a friendly SMS."""
    command = request.form.get('command')
    print(request.form)

    # Start our response
    resp = MessagingResponse()

    global safety

    if command == 'check_safety':	# when the pi detect stanger
    	send_message("Hey Yuanwei, we detect your car is moving. Is that under your permission?")
    	return "Hey Yuanwei, we detect your car is moving. Is that under your permission?"
    elif not command: 				# reply from mobile
    	text = request.form.get('Body')
    	if text == 'yes':
    		resp.message("Okay, never mind.")
    		safety = True
    	elif text == 'stop update':
    		safety = True
    	elif text == 'update':
    		safety = False
    	else:
    		resp.message("Ok, I will tell police to track your car.")
    		safety = False
    	return str(resp)
    elif command == 'update':
    	localization = request.form.get('Localization')
    	current_time = request.form.get('time')
    	print(current_time + '\n' + localization)
    	send_message(current_time + '\n' + localization)

    return str(resp)

@app.route("/safe", methods=['GET', 'POST'])
def check_safety():
	return str(safety)

if __name__ == "__main__":
    app.run(debug=True)