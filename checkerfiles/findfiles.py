#!/usr/bin/env python
'''

Crawler to search and find files within specified location. 

'''

import multiprocessing as mp
import os, sys
import time



def explore_path(path):
	directories = []
	nondirectories = []
	try:
		for filename in os.listdir(path):
			fullname = os.path.join(path, filename)
			if os.path.isdir(fullname):
				directories.append(fullname)
			elif os.path.exists(fullname):
				nondirectories.append(fullname)
			else:
				print 'Permission denied or broken symlink: ', path
	except OSError:
		print 'Permission denied: ', path
		pass	
	except:
		print 'Unknown error: ', path
		pass

	return directories, nondirectories



def parallel_worker(i, unsearched, found):
	scan = WhatIsHere()
	while True:
		if unsearched.empty() == False:
			path = unsearched.get()
			dirs, files = explore_path(path)
			for file in files:
				scan.add(file)
				if file.endswith('.nc'):
					scan.ncfiles.append(file)

			for newdir in dirs:
				unsearched.put(newdir)
			unsearched.task_done()
		else:
			time.sleep(5)
			if unsearched.empty() == True:
				break
	
	found.put(scan)
 

def find_files(path):
	#path = sys.argv[1]
	#print 'Checking under directory: ', path

	m = mp.Manager()
	unsearched = mp.JoinableQueue()
	found = m.Queue()
	unsearched.put(path)

	try:
		np = 7
		jobs = []
		for i in range(np):	
			p = mp.Process(target=parallel_worker, args=(i, unsearched, found))
			jobs.append(p)
		for p in jobs:
			p.start()

		for p in jobs:
			p.join()
		unsearched.join()	

		print 'Getting results...'
		results = [found.get() for p in jobs]
		# sum up results here before returning them *****

		ncfiles = []
		totals = {}
		for result in results:
			for item in result.ncfiles:
				ncfiles.append(item)

			for key in result.found.keys():
				if key not in totals.keys():
					totals[key] = result.found[key]
				else:
					totals[key]['count'] += result.found[key]['count']
					totals[key]['size']  += result.found[key]['size']

	
	except:	
		for p in jobs:
			p.terminate()
		sys.exit('Opps something happened- ending processes and exiting...')

	
	return ncfiles, totals



class WhatIsHere:
	def __init__(self):
		self.found = {}
		self.ncfiles = []

	def add(self, fullpath): 
		try:
			size = os.stat(fullpath)[6]
			name = os.path.basename(fullpath)

			if name.count('.') != 0:
				ext = name.split('.')[-1].lower()
				try:
					i = int(ext)
					ext = '(numeric)'
				except ValueError:
					pass	
			else:
				ext = '(no_extension)'				

			if ext in self.found.keys():
				self.found[ext]['count'] += 1
				self.found[ext]['size'] += size
			else:
				self.found[ext] = {'count': 1, 'size': size}

		except:
			print "Problem reading: ", fullpath
			pass


#if __name__ == '__main__':
#	
#	r = find_files()
#	for item in r:
#		print item.ncfiles

