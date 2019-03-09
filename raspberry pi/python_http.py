import requests
import time


r = requests.post("https://415848bd.ngrok.io/sms", \
	data={'command': 'check_safety'})

while True:
	r = requests.post("https://415848bd.ngrok.io/safe")
	print(r.status_code, r.reason)
	print(r.text[:300] + '...')
	if r.text == 'False':
		current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		r = requests.post("https://415848bd.ngrok.io/sms", \
			data={'command': 'update', \
				  'Localization': 'Latitude： 47.606209, longitude: -122.332069', \
				  'time': current_time})
	time.sleep(10)