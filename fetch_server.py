
#!/usr/bin/env python


# fetch server frontend

import os
import threading
import time

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import fetch_local_monitor
import fetch_remot_monitor

import zmq

define("port", default=8483, type=int)

monitor_servers = ["tcp://localhost:5555", "tcp://localhost:6666"]
heartbeat_servers = ["tcp://localhost:5556", "tcp://localhost:6667"]



class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/local", fetch_local_monitor.FetchHandler),
			(r"/remot", fetch_remot_monitor.FetchRemoteMonitorHandler),
		]

		settings = dict(
			title = "Fetching",
			base_url = "http://localhost:8483",
			static_path = os.path.join(os.path.dirname(__file__), "static")
		)

		tornado.web.Application.__init__(self, handlers, **settings)


def check_monitor_status():
	context = zmq.Context()
	poller  = zmq.Poller()

	current_monitor_index = 0

	heartbeat = context.socket(zmq.REQ)
	heartbeat.connect(heartbeat_servers[current_monitor_index])
	poller.register(heartbeat, zmq.POLLIN)

	while True:
		# send heartbeat signal every x seconds
		heartbeat.send("")

		socks = dict(poller.poll(1 * 1000))

		if socks.get(heartbeat) == zmq.POLLIN:
			heartbeat.recv()
		else:
			print "switch monitor server"
			current_monitor_index = (current_monitor_index+1) % len(monitor_servers)
			
			poller.unregister(heartbeat)
			heartbeat.setsockopt(zmq.LINGER, 0)
			heartbeat.close()
			

			heartbeat = context.socket(zmq.REQ)
			heartbeat.connect(heartbeat_servers[current_monitor_index])
			poller.register(heartbeat, zmq.POLLIN)

			fetch_remot_monitor.change_server_addr( monitor_servers[current_monitor_index] )

		time.sleep(1)


def main():
	fetch_remot_monitor.change_server_addr(monitor_servers[0])

	thread = threading.Thread(target=check_monitor_status, args=())
	thread.start()

	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()



if __name__ == '__main__':
	main()