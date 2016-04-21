#!/usr/bin/env python

'''

The main multiprocessing worker. The following routine and subroutines
run simultaneously to check compliance of the files specified. Two main 
categories are check: (1) Attribute Convention for Data Discovery (ACDD)
compliance and (2) Climate and Forcast (CF) Convention compliance. 

'''
import multiprocessing as mp
import os, sys
import metadata, output, cfwrapper, findfiles
from cfchecks import CFVersion, CFChecker
from contextlib import contextmanager
import resource
from guppy import hpy


STANDARDNAME = 'http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml'
AREATYPES = 'http://cfconventions.org/Data/area-type-table/current/src/area-type-table.xml'
udunits=None
areaTypes=AREATYPES
version=CFVersion()



''' 
Used to redirect the output from the CF-Convention checker
so that the cfwrapper can combine results of all files scanned   '''
@contextmanager
def redirected(stdout):
	saved_stdout = sys.stdout
	sys.stdout = open(stdout, 'w')
	yield
	sys.stdout = saved_stdout




''' 
The main class for checking the files. It:
   (1) 'getAllFiles' --> finds the files
   (2) 'worker' --> does the checking (is split over multiple processes)
'''
class check:

	def __init__(self):
		self.fileQueue = mp.Queue()
		self.cf = mp.Queue()
		self.meta = mp.Queue()
		self.fileList = []
		self.skipped = mp.Queue()
		self.filetypes = {} # {'nc':{'capacity':0, 'count':0}}
	
	

	'''--------------------------------------------------------------
	Finds the files to check. Uses 'findfiles.py' and it searches 
	under the defined path using the python multiprocessing library. 
	As it searches, it also keeps track so of the different file
	types and total size per type. 
	--------------------------------------------------------------'''
	def getAllFiles(self, path, nf):
		# If path is a directory --> continue and search under path
		if os.path.isdir(path):	
			# Calls 'findfiles.py' to crawl the directory
			self.fileList, self.filetypes = findfiles.find_files(path)
						
			if nf == 'all':
				pass # list already contains all files to check
			elif nf:
				del self.fileList[nf:]
			else:
				if len(self.fileList) > 1:
					ask = raw_input('More than '+str(1)+' .nc file found. Check more of the '+str(len(self.fileList))+' files found? (y/n)')
					if ask == 'y':
						limit = raw_input("How many total? (enter # of files or 'a' for all): ")
						if limit.isdigit() == True:
							del self.fileList[int(limit):]
					else:
						del self.fileList[1:]
		
		

		# Else if just one file specified
		else:
			self.fileList.append(file)			
		
		
		# Finalise queue
		for file in self.fileList:
			self.fileQueue.put(file)		


	'''--------------------------------------------------------------
	Multiprocessing part: This worker function scans and checks
	compliance in parallel for the number of processes (np) defined.
	Metadata will be checked using metadata.py while CF compliance is
	checked using a wrapper (cfconvention.py) to the CF-Convention
	checker (cfchecks.py). 
	--------------------------------------------------------------'''
	def worker(self, cpu, tmpdir, sn):
		print 'Process: '+str(cpu)+' started.' 	

		# Initiate metadata tracking
		meta = metadata.meta_check() 
		cf = cfwrapper.cf()

		# Initialise counters	
		kk = 0
		skipped = []

		# Create tmp log for this process
		tmplog = output.tmplog(cpu, tmpdir)

		'''
		-------------------------------------------------
		While the fileList queue still has files: check
		------------------------------------------------- '''	
		while self.fileQueue.empty() == False:
			try:
				# Try to get a file off the file queue, if successful continue
				ncfile = self.fileQueue.get()
				print "{:<14}{:^5}{:<15}{:>15}{:^5}".format('[PROCESS: **', cpu, ' **]', 'Checking file: ', kk+1)
				print resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
			except:
				break	

			

			tmplog.header(ncfile)				
							
			# Open/read file and extract global attributes, netCDF format
			#gatts, ncformat, conv, vars = readfile.read(ncfile)
			f = metadata.read(ncfile)

			tmplog.meta(f.atts, f.ncformat, f.conv)
			
			# Initialise CF and ACDD lists on first loop then check 
			# if variables the same between each file on subsequent loops.
			cf.newvars(f.vars.keys())
							
		
			# ACDD Compliance Check
			# Check list against global file attributes, track sum of missing acdd attrs
			meta.acddCheck(f.atts)	
				
			# Also keep track of file netCDF format and conventions used (if any)
			meta.fileFormat(f.ncformat)
			meta.conventions(f.conv)

			# Check for coordinate variables and spatial info
			meta.spatialCheck(f.vars)		
			meta.coordvarCheck(f.dims, f.vars.keys())
			meta.stdnamesCheck(f.vars)
			'''
			-------------------------------------------------------
			Wrapper for CF-Convention 'cfchecks.py' 
			-------------------------------------------------------'''
			# Run the 'cfchecks.py' script on the individual file, redirect output to tmpfile
			tmpfile = tmpdir+'/tmp'+str(cpu)+'.out'
			
			# Check for new standard name table first
			if not sn: 
				standardName=STANDARDNAME
			else:
				standardName=sn
			
			# This line initialises cfchecks.py
			inst = CFChecker(uploader=None, useFileName="yes", badc=None, coards=None, cfStandardNamesXML=standardName, cfAreaTypesXML=areaTypes, udunitsDat=udunits, version=version)

			# This part executes the checker part of cfchecks.py and redirects output to tmpfile
			# If for any reason a file can't be read, keep track of that 
			rc = []
			with redirected(stdout=tmpfile):
				try:
					inst.checker(ncfile)
				except:
					rc = 0
			
			if rc == 0:
				print 'Unexpected error: ', sys.exc_info()[0], sys.exc_info()[1]
				print '\nFILE: '+ncfile+' [SKIPPING FILE]\n'
				skipped.append(ncfile)

			cf.wrapper(tmplog, tmpfile)	
					
			print >>tmplog.fn, ' \n'
			kk += 1
			
			

		# If results from this process, add to local result queue
		#try:					
		self.meta.put(meta)
		self.cf.put(cf)
		self.skipped.put(skipped)
		print 'Process: '+str(cpu)+' completed.'


	 


