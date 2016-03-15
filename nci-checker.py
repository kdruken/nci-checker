#!/usr/bin/env python

'''
---------------------------------------------------------------
@author: K. Druken- NCI (kelsey.druken@anu.edu.au)
Date Created:   20-Nov-2015
Version: 4


---------------------------------------------------------------
Non-standard Dependencies:
    Python modules: numpy, netCDF4, cdms
    Libraries: udunits

Initial setup: 
    See readme file for more detailed information. Before 
    running code for first time, the udunits2 library path 
    might need to be added on your system. The 'udunits' 
    library name may also need modification if using on OSX. 
    See the 'cfchecks.py' included in checkerfiles/ and 
    comment/uncomment appropriate line for your system.
 
--------------------------------------------------------------
'''
from checkerfiles import *
import tempfile, shutil


'''--------------------------------------------------------------
Help/usage message
--------------------------------------------------------------'''
def help():
	''' 

	Usage: python nci-checker.py [OPTIONS] file/directory

	       (No flag required before listing a filename.) 

	Options:

	--help 		Print this usage message and exit
	--dir 		Specifiy before directory to check entire contents
	--np 		Specifiy the number of python multiprocesses 
			to use (default np = 8)
	--log 		Save detailed output
	--brief 	Save brief summary output
	--debug		Do not delete the tmp files for debugging

	'''


'''--------------------------------------------------------------
Get user inputs
--------------------------------------------------------------'''
class getinputs(object):
	def __init__(self, argv):
		# If no inputs given, print help info and exit
		if len(argv) < 2:
			print help.__doc__	
			sys.exit()
		
		# '--help', print how to use this tool
		helpStr = ['--help']
		for item in argv:
			if item in helpStr:
				print help.__doc__
				sys.exit()		
				
		# Directory with 'nc' files to check, will be second input value
		self.filesdir = []
		self.file = []
		for j in range(0, len(argv)):
			# '--dir' specifies top directory to check
			if argv[j] == '--dir':
				self.filesdir = str(argv[j + 1])

			elif '.nc' in argv[j]:
				self.file = str(argv[j])
		
		if not self.file and not self.filesdir:
			sys.exit("No directory or file given. Provide '.nc' file or use '--dir' followed by directory path.")
		
			
		# '--np' specifies the number of processes to run, default is np=8
		if argv.count('--np') == 1:
			self.ncpu = int(argv[argv.index('--np')+1])
		else:
			self.ncpu = 8
		
		# '--log' or '--brief' specifies long/short log option of output
		if argv.count('--log') == 1:
			self.log = 'y'
		elif argv.count('--brief') == 1:
			self.log = 'b'
		else:
			self.log = 'n'
			

		# '--debug': flag for debugging, leaves tmp files
		if argv.count('--debug') == 1:
			self.debug = 1
		else:	
			self.debug = 0

		
		# '--nci_snt' specifies to use nci version of standard name table
		for i in range(0, len(argv)):
			if argv.count('--nci_snt') == 1:
				# This is currently a copy of the CF standard name table but 
				# can be used to extend CF standard names in future work.
				self.sn = './checkerfiles/nci-standard-name-table.xml'
			else:
				self.sn = []

		# '-v' specifices CF-Convention version to check against 
		# (default is most recent if not specified within file)
		if argv.count('--v') == 1:
			self.cfver = int(argv[argv.index('--v')+1])
		else:
			self.cfver = 'auto'

		
'''--------------------------------------------------------------
Use to sum final totals 
--------------------------------------------------------------'''
class finalSum(object):
	def __init__(self):
		self.err = {}
		self.warn = {}
		self.info = {}
		self.req = {}
		self.rec = {}
		self.sug = {}
		self.other = {}
		self.format = {}
		self.conv = {}
		self.total = {}
		
	def sum(self, attr, dict2):
		dict1 = self.__dict__[attr]
		for item in dict2.keys():
			if item in dict1.keys():
				dict1[item] = dict1[item] + dict2[item]
			else:
				dict1[item] = dict2[item]
		self.__dict__[attr] = dict1


	
	

'''--------------------------------------------------------------
To calculate report score 
--------------------------------------------------------------'''	
class scoring():
	def __init__(self):
		self.err = 0
		self.warn = 0
		self.info = 0
		self.req = 0
		self.rec = 0
		self.sug = 0
		self.other = 0
		self.format = 0
		self.conv = 0

 	
	def calc(self, result, nfiles, nskip):
		cflist = ['err', 'warn', 'info']
		for attr, score in self.__dict__.items():
			for key, item in result.__dict__[attr].items():	
				if attr in cflist:
					try:
						score += float(item)/result.__dict__['total'][key]
					
					except ZeroDivisionError:
						score = 0
						
				elif key != 'total':
					score += float(item)/nfiles
		
			try:
				self.__dict__[attr] = score/len(result.__dict__[attr])

			except ZeroDivisionError:
				''' Dataset may not contain additional metadata '''
				print "Zero division error: Empty '", attr, "' dictionary"
				self.__dict__[attr] = 0



'''--------------------------------------------------------------
Main Program
--------------------------------------------------------------'''	
def main():
	start_time = datetime.now()

	# Make a temporary directory
	workdir = os.path.dirname(os.path.abspath(__file__))
	tmpdir = tempfile.mkdtemp(prefix='tmp', dir=workdir)

	'''--------------------------------------------------------------
	Get user inputs, initialise queues, and determine number of 
	processes to split jobs across. 
	--------------------------------------------------------------'''
	inputs = getinputs(sys.argv)	

	# Define queues for all the data/metadata reporting
	# that need saving from each process
	run = checkfiles.check()
	
	print "Searching directory and subdirectories for '.nc' files..."
	run.getAllFiles(inputs.filesdir, inputs.file)


	# If number of files is less than requested 'np', reduce to np = total # files
	if inputs.ncpu > len(run.fileList):
		inputs.ncpu = len(run.fileList)


	'''--------------------------------------------------------------
	Setup, run, join, and retrieve results for output
	--------------------------------------------------------------'''	
	# Print job info
	output.begin(inputs.filesdir, inputs.file, inputs.ncpu)

	# Setup a list of processes that we want to run
	print "Initiating multiprocesses..."
	processes = []
	for x in range(0, inputs.ncpu):
		p = mp.Process(target=run.worker, args=(x, tmpdir, inputs.sn))
		processes.append(p)

	# Run processes
	print "Starting multiprocesses..."
	print ""
	for p in processes:
		p.start()

	# Exit the completed processes
	for p in processes:
		p.join()
	
	print ""
	print "Joining multiprocesses..."
	print ""
	# Get process results from the output queue
	CF = [run.cf.get() for p in processes]
	META = [run.meta.get() for p in processes]
	ERR = [run.fileErr.get() for p in processes]
	

	# Combine the list of any files that could not be read
	fileErr = []
	for proc in range(0, inputs.ncpu):
		if ERR[proc]:
			for item in ERR[proc]:
				fileErr.append(item)

	if len(fileErr) == len(run.fileList):
		shutil.rmtree(tmpdir)
		sys.exit("NO FILES COULD BE READ. EXITING.")

	'''--------------------------------------------------------------
	Sum totals and print output
	--------------------------------------------------------------'''
	results = finalSum()
	for proc in range(0, inputs.ncpu):
		for attr in results.__dict__.keys():
			try:
				if attr in ['err', 'warn', 'info', 'total']:
					results.sum(attr, CF[proc].__dict__[attr])
				else:
					results.sum(attr, META[proc].__dict__[attr])
	
			except AttributeError:						
				''' 
				If the processes scan out of order or at different rates
				some will not have output to sum together, so pass.
				'''
				print 'Process: '+str(proc)+', no results from this process to sum.'
				pass


	

	'''--------------------------------------------------------------
	Calculate report scoring
	--------------------------------------------------------------'''	
	score = scoring()
	score.calc(results, len(run.fileList), len(fileErr))

	
	'''--------------------------------------------------------------
	Print output to report and screen
	--------------------------------------------------------------'''	
	log, inputs.fn_out = output.header(workdir, inputs.filesdir, inputs.file, len(run.fileList), len(fileErr))
	output.report(results, score, log, len(run.fileList))
	output.screen(inputs.fn_out)
	output.append(tmpdir, inputs.fn_out, inputs.log, inputs.ncpu, fileErr)


	'''--------------------------------------------------------------
	Cleanup and exit
	--------------------------------------------------------------'''
	# Either way, delete temp files before exiting (unless in debug mode)
	if inputs.debug == 0:
		print 'Removing temp files...'
		shutil.rmtree(tmpdir)
		print 'Done.'
	
	# Display total duration for compliance check 
	end_time = datetime.now()
	print('Duration: {}'.format(end_time - start_time))


if __name__ == '__main__':
	main()

