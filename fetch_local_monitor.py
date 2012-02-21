

#!/usr/bin/env python

import tornado.httpserver
import tornado.httpclient
import tornado.web

from monitor import Monitor

# initialize the user activity monitor
monitor = Monitor()



class FetchHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		url = self.get_argument("url", None)
		caller = self.request.remote_ip
		
		if not url: return
		
		# check malicious user
		if not monitor.check(url):
		   print "malicious user detected: [", url, "]\n"
		   return

		# async
		http = tornado.httpclient.AsyncHTTPClient()
		http.fetch(url, callback=self.on_response)

	def on_response(self, response):
		# misbehaving servers
		if response.error:
			if response.error.code == 599:
			   pass
			elif response.error.code == 404:
			   pass
			raise tornado.web.HTTPError(500)
		
		#print response.body
		self.write(response.body)
		self.finish()