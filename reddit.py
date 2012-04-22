from json import loads
from urllib2 import build_opener
from urllib2 import HTTPCookieProcessor
from urllib import urlencode
from time import sleep
from cookielib import CookieJar


class Reddit(object):

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.cj = CookieJar()
		self.opener = build_opener(HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]


	def browse(self, url):
		self.url = self.opener.open(url)
		self.lg_data = loads(self.url.read())
		self.url.close()
		return self.lg_data


	def send(self, action, params):
		#proxy settings  
		self.params = urlencode(params)
		self.api  = "http://www.reddit.com/api/%s"%(action)
		#self.opener.addheader('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0)')
		self.resp = self.opener.open(self.api, self.params)		
		self.data = self.resp.read()
		self.resp.close()
		#print action, "=========>", self.data
		sleep(5)
		self.json = loads(self.data)
		errors = self.json['json']['errors']
		if errors:
			print action, "ERROR:", errors[0][0], errors[0][1]
		else:
			print action,": SUCCESS"
		return self.json

	def login(self):
		self.params = {"user":self.username, "passwd":self.password, "api_type":"json"}
		self.json_data = self.send("login/%s"%self.username, self.params)
		return self.json_data

	def post(self, uh, thing_id, text):
		self.thing_id = thing_id
		self.text = text
		self.uh = uh['json']['data']['modhash']
		self.comment_url = "http://www.reddit.com/api/comment" 
		self.params2 = {"thing_id":self.thing_id, "text":self.text, "uh":self.uh, "api_type":"json"}
		self.send("comment", self.params2)