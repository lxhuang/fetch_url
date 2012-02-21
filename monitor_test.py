#!/usr/bin/env python

from monitor import Monitor
import random
import time

def load_tester():
	count = 1
	monitor = Monitor()
	while True:
		monitor.check(str(count))
		count = count + 1

def random_tester():
	monitor = Monitor()
	while True:
		user = random.randint(1,30)
		if not monitor.check(str(user)):
			print "malicious user detected"
		time.sleep(0.05)


if __name__ == "__main__":
	#load_tester()
	random_tester()