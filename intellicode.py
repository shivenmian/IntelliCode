import os
import config
import time
import requests
import urllib
from slackclient import SlackClient
from google import search
from lxml import html
import cssselect

botname = 'intellicode' 
client_slack = SlackClient(config.slack_token['SLACK_TOKEN'])

def bot_id():
	api_call = client_slack.api_call("users.list")
	if api_call.get('ok'):
		members = api_call.get('members')
		for user in members:
			if 'name' in user and user.get('name') == botname:
				return user.get('id')

def parse_data(slack_data):
	inputdata = slack_data
	if inputdata and len(inputdata) > 0:
		for data in inputdata:
			if data and 'text' in data and data['user']!=bot_id():
				return data['text'], data['channel']
	return None, None

def chat(inputcmd, channel):
	#botid = "<@" + str(bot_id()) + ">:"
	soverflowurl = "http://stackoverflow.com"
	for url in search(urllib.quote_plus(inputcmd.encode('utf8'))):
		if "http://stackoverflow.com/" in url:
			soverflowurl = url;
			break
		else:
			continue
	try:
		r = requests.get(soverflowurl)
		pagecode = html.fromstring(r.content)
		output = "```" + pagecode.cssselect('div.accepted-answer pre code')[0].text + "```"
		client_slack.api_call("chat.postMessage", channel = channel, text = output, as_user = True)
	except IndexError:
		r = requests.get(soverflowurl)
		pagecode = html.fromstring(r.content)
		output = "```" + pagecode.cssselect('td.answercell div.post-text code')[0].text + "```"
		client_slack.api_call("chat.postMessage", channel = channel, text = output, as_user = True)
	except:
		print("Could not parse")
		raise

def intellicode():
	if client_slack.rtm_connect():
		print("Connected")
		while True:
			inputcmd, channel = parse_data(client_slack.rtm_read())
			if inputcmd and channel:
				chat(inputcmd, channel)
			time.sleep(1)
	else:
		print("Connection failed")

if __name__ == '__main__':
	intellicode()
