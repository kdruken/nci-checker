#!/usr/bin/env python

'''

The main multiprocessing worker. The following routine and subroutines
run simultaneously to check compliance of the files specified. Two main 
categories are check: (1) Attribute Convention for Data Discovery (ACDD)
compliance and (2) Climate and Forcast (CF) Convention compliance. 

'''
import multiprocessing as mp
import os
import metadata, readfile, output, cfconvention



class check:
	
	def __init__(self):
		self.fileQueue = mp.Queue()
		self.cf = mp.Queue()
		self.meta = mp.Queue()
		self.fileList = []



	def getAllFiles(self, filesdir, file):
		
		# If dir defined, walk thru subdirectories and find '.nc' files for cfchecker
		if filesdir:
			for root, dirs, files in os.walk(filesdir, topdown=False, followlinks=True):
				for name in files:
					if name.endswith('.nc'):
						self.fileList.append(os.path.join(root, name))
		
			limit = 1
			if len(self.fileList) > limit:
				ask = raw_input('More than '+str(limit)+' .nc file found. Check more of the '+str(len(self.fileList))+' files? (y/n): ')
				if ask == 'y':
					limit = raw_input("How many total? (enter # of files or 'a' for all): ")
					if limit.isdigit() == True:
						del self.fileList[int(limit):]
				else:
					del self.fileList[limit:]
		
		# Else if just one file specified
		elif file:
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
		script = './checkerfiles/cfchecks.py' 

		# Initiate metadata tracking
		meta = metadata.meta_check() 
		cf = cfconvention.cf()

		# Equals zero until a file is checked, then tracks total number 
		# for this process	
		kk = 0
		
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
				tmplog.header(ncfile)				
				
								
				# Open/read file and extract global attributes, netCDF format
				gatts, ncformat, vars = readfile.read(ncfile)
				tmplog.meta(gatts, ncformat)
				
				# Initialise CF and ACDD lists on first loop then check 
				# if variables the same between each file on subsequent loops.
				cf.newvars(vars)
								
			
				# ACDD Compliance Check
				# Check list against global file attributes, track sum of missing acdd attrs
				meta.acddCheck(gatts)	
					
				# Also keep track of file netCDF format
				meta.saveFormat(ncformat)		

				'''
				-------------------------------------------------------
				Wrapper for CF-Convention 'cfchecks.py' 
				-------------------------------------------------------'''
				# Run the 'cfchecks.py' script on the individual file
				# Check for new standard name table first
				tmpfile = tmpdir+'/tmp'+str(cpu)+'.out'
				
				if not sn:
					os.system(script+' '+ncfile+' > '+tmpfile)
				else:
					os.system(script+' -s '+sn+' '+ncfile+' > '+tmpfile)

				
				cf.wrapper(tmplog, tmpfile)	
						
				print >>tmplog.fn, ' \n'
				kk += 1
			
			except:
				break	

		# If results from this process, add to local result queue
		try:					
			self.meta.put(meta)
			self.cf.put(cf)
			print 'Process: '+str(cpu)+' completed.'

		except UnboundLocalError, err1:
			print 'Process: '+str(cpu)+', UnBoundLocalError has occurred: ', err1

		except:
			print "Unexpected error: ", sys.exc_info()[0], sys.exc_info()[1]
	 


