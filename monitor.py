#!/usr/bin/env python

# monitor the request frequency from users

import time
import threading

def clean_routine(mem, index):
	mem.clear()
	#print "cache ", index, " is empty\n"

class Monitor:
	def __init__(self, space=1000, allowed_violation=5, capacity=10000, block_time=1):
		# allowed item number in the cache
		self.max_size = capacity 
		
		# requests from single user should space out by 1s (default), 
		# and you cannot violate the rule more than 5 (default) times
		self.proper_space = space
		self.allowed_violation = allowed_violation
		self.block_time = block_time

		# caches
		self._cache1 = {}
		self._cache2 = {}
		# store malicious user
		self.malicious_user = {}

		self.cache = self._cache1
		self.cache_index = 1

	def check(self, user):
		
		now = time.time()*1000

		#print "[", user, "] ", now, "\n"

		# access malicious_user and check
		if user in self.malicious_user:
			if (now - self.malicious_user[user] > 1000*60*self.block_time): # wait for certain time
				del self.malicious_user[user]
			else:
				self.malicious_user[user] = now
				return False


		# access the current cache
		if user not in self.cache:
			self.cache[user] = [now, 1]
		else:
			if (now - self.cache[user][0] < self.proper_space):
				repeat = self.cache[user][1]
				if (repeat + 1 > self.allowed_violation):
					self.malicious_user[user] = now
					del self.cache[user]
					return False
				else:
					self.cache[user][0] = now
					self.cache[user][1] = repeat + 1
			else:
				self.cache[user][0] = now

		# debug
		#print self.cache
		

		# if the current cache is full, switch
		if len(self.cache) == self.max_size:
			#print "cache ", self.cache_index, " is full, now switching...\n"
			if self.cache_index == 1:
				self.cache = self._cache2
				self.cache_index = 2
				thread = threading.Thread(target=clean_routine, args=(self._cache1, 1, ))
				thread.start()
			else:
				self.cache = self._cache1
				self.cache_index = 1
				thread = threading.Thread(target=clean_routine, args=(self._cache2, 2, ))
				thread.start()
		
		return True

