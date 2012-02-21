

#!/usr/bin/env python

import sys
import zmq

from monitor import Monitor

def main():
	
	argc = len(sys.argv)
	if argc < 2:
		print "usage: python monitor_server port"
		return
	else: 
		server_port = int(sys.argv[1])

	monitor = Monitor()

	context = zmq.Context()
	
	# monitor server
	server = context.socket(zmq.ROUTER)
	server.bind("tcp://*:" + str(server_port))

	# heartbeat
	heartbeat = context.socket(zmq.ROUTER)
	heartbeat.bind("tcp://*:" + str(server_port+1))

	poller = zmq.Poller()
	poller.register(server, zmq.POLLIN)
	poller.register(heartbeat, zmq.POLLIN)

	while True:
		socks = dict(poller.poll())

		if socks.get(server) == zmq.POLLIN:
			addr = server.recv()
			tmp  = server.recv()
			data = server.recv()

			print data

			server.send(addr, zmq.SNDMORE)
			server.send("", zmq.SNDMORE)
			if monitor.check(data):
				server.send("pass")
			else:
				server.send("fail")
		elif socks.get(heartbeat) == zmq.POLLIN:
			addr = heartbeat.recv()
			tmp  = heartbeat.recv()
			data = heartbeat.recv()

			print "heartbeat"

			heartbeat.send(addr, zmq.SNDMORE)
			heartbeat.send("", zmq.SNDMORE)
			heartbeat.send("live")


if __name__ == "__main__":
	main()