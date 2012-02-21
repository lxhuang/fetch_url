

#!/usr/bin/env python

import zmq
import memcache

import tornado.httpserver
import tornado.httpclient
import tornado.web

server_addr = ""

mc = memcache.Client(["127.0.0.1:11211"], debug=0)

def change_server_addr(new_addr):
	global server_addr
	server_addr = new_addr

class FetchRemoteMonitorHandler(tornado.web.RequestHandler):
	
	def check_malicious_user(self, user):
		ret = False
		context = zmq.Context()
		client = context.socket(zmq.REQ)
		client.connect(server_addr)
		
		poller = zmq.Poller()
		poller.register(client, zmq.POLLIN)

		client.send(user)
		print "checking ", user

		socks = dict(poller.poll(1 * 1000)) # wait no more than x seconds

		if socks.get(client) == zmq.POLLIN:
			message = client.recv()
			if message == "pass":
				ret = True
		
		poller.unregister(client)
		client.setsockopt(zmq.LINGER, 0)
		client.close()

		return ret


	def get(self):
		url = self.get_argument("url", None)
		caller = self.request.remote_ip

		if not url: return

		memcache_key = str(url)

		#check malicious user
		ret = ""
		if self.check_malicious_user(caller):
			# check memcache
			cache_content = mc.get(memcache_key)
			if cache_content:
				print memcache_key, " <- cached"
				ret = cache_content
			
			else:
				try:
					http = tornado.httpclient.HTTPClient()
					response = http.fetch(url)
					ret = response.body

					mc.set(memcache_key, ret, 30)

				except tornado.httpclient.HTTPError, e:
					print "Error code: ", e.code

					mc.set(memcache_key, "", 60)
					
					ret = ""
		else:
			ret = ""
		
		self.write(ret)
		self.finish()


