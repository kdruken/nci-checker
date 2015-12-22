#!/usr/bin/env python

'''
---------------------------------------------------------------
@author: K. Druken- NCI (kelsey.druken@anu.edu.au)
Date Created:   20-Nov-2015
Version: 4

Last modified:  20-Nov-2015


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
	--fn 		Specify prefix of log/brief filename (default = datetimestamp)
	--debug		Do not delete the tmp files for debugging

	'''


'''--------------------------------------------------------------
Get user inputs
--------------------------------------------------------------'''
def getinputs():
	# If no inputs given, print help info and exit
	if len(sys.argv) < 2:
		print help.__doc__	
		sys.exit()
	
	# '--help', print how to use this tool
	helpStr = ['--help']
	for item in sys.argv:
		if item in helpStr:
			print help.__doc__
			sys.exit()
			
	# Directory with 'nc' files to check, will be second input value
	filesdir = file = []
	for j in range(0, len(sys.argv)):
		# '--dir' specifies top directory to check
		if sys.argv[j] == '--dir':
			filesdir = str(sys.argv[j + 1])
			print filesdir
		elif '.nc' in sys.argv[j]:
			file = str(sys.argv[j])
	
	if not file and not filesdir:
		sys.exit("No directory or file given. List .nc file or use '--dir' followed by directory path.")
	
		
	# '--n' specifies the number of processes to run, default is n=8
	if sys.argv.count('--np') == 1:
		ncpu = int(sys.argv[sys.argv.index('--np')+1])
	else:
		ncpu = 8
	
	# '--log' or '--brief' specifies long/short log option of output
	if sys.argv.count('--log') == 1:
		detailed_log = 'y'
	elif sys.argv.count('--brief') == 1:
		detailed_log = 'b'
	else:
		detailed_log = 'n'
		
	# '--fn' specifies log file name (not required)
	if sys.argv.count('--fn') == 1:
		fn_out = str(sys.argv[sys.argv.index('--fn')+1])
	else:
		fn_out = []

	# '--debug': flag for debugging, leaves tmp files
	if sys.argv.count('--debug') == 1:
		debug = 1
	else:	
		debug = 0
		

	return filesdir, file, ncpu, detailed_log, fn_out, debug



'''--------------------------------------------------------------
Initialise list of .nc files to check within directory
--------------------------------------------------------------'''
def getAllFiles(filesdir, file, fileList, q):
	# If dir defined, walk thru subdirectories and find '.nc' files for cfchecker
	if filesdir:
		for root, dirs, files in os.walk(filesdir, topdown=False, followlinks=True):
			for name in files:
				if name.endswith('.nc'):
					fileList.append(os.path.join(root, name))
	
		limit = 1
		if len(fileList) > limit:
			ask = raw_input('More than '+str(limit)+' .nc file found. Check more of the '+str(len(fileList))+' files? (y/n): ')
			if ask == 'y':
				limit = raw_input("How many total? (enter # of files or 'a' for all): ")
				if limit.isdigit() == True:
					del fileList[int(limit):]
			else:
				del fileList[limit:]
	
	# Else if just one file specified
	elif file:
		fileList.append(file)			
	
	
	# Finalise queue
	for file in fileList:
		q.put(file)			
	
'''--------------------------------------------------------------
Initialise CF variable
--------------------------------------------------------------'''
class initCF(object):
	def __init__(self, vars):
		vars.append('global')
		self.err = dict.fromkeys(vars, 0)
		self.warn = dict.fromkeys(vars, 0)
		self.info = dict.fromkeys(vars, 0)
		self.total = dict.fromkeys(vars,0)
	
	def newvars(self, vars):
		for var in vars:
			if var not in self.err.keys():
				self.err[var] = 0
				self.warn[var] = 0
				self.info[var] = 0
				self.total[var] = 0

	
		
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
Check for particular standard variable name standards

** This is a modification to CF-compliance where new standard
variable libraries have been developed to expand CF-like
compliance for other geosciences.

** 20-Nov-2015: This new table does not yet exist, but process
				in place to work with this compliance tool. 
--------------------------------------------------------------'''	
def stdNameTable():
	for i in range(0, len(sys.argv)):
		# '--nci_snt' specifies to use nci version of standard name table
		if sys.argv.count('--nci_snt') == 1:
			sn = './checkerfiles/nci-standard-name-table.xml'
		else:
			sn = []
	return sn
		


'''--------------------------------------------------------------
Run the NetCDF Climate Forcast Conventions compliance checker
version 2.0.9 over each '.nc' file found under the specified
directory. Information on 'cfchecks.py' can be found at:

https://pypi.python.org/pypi/cfchecker/2.0.9
--------------------------------------------------------------'''	
def worker(cpu, q, cfQ, metaQ, tmpdir): 
	print 'Process: '+str(cpu)+' started.' 
	script = './checkerfiles/cfchecks.py' 

	# Initiate metadata tracking
	meta = metadata.meta_check() 	
	cf = []
	#for kk in range(0, chunkSize):
	kk = 0

	'''
	-------------------------------------------------
	While the fileList queue still has files: check
	------------------------------------------------- '''	
	while q.empty() == False:
		try:
			ncfile = q.get()
			print "{:<14}{:^5}{:<15}{:>15}{:^5}".format('[PROCESS: **', cpu, ' **]', 'Checking file: ', kk+1)
			
			# Run the 'cfchecks.py' script on the individual file
			# Check for new standard name table first
			sn = stdNameTable()
			tmpfile = tmpdir+'/tmp'+str(cpu)+'.out'
			if not sn:
				os.system(script+' '+ncfile+' > '+tmpfile)
			else:
				os.system(script+' -s '+sn+' '+ncfile+' > '+tmpfile)
			
			tmplog = output.tmplog(cpu, ncfile, tmpdir)

			# Open/read file and extract global attributes, netCDF format
			gatts, ncformat, vars = readfile.read(ncfile)
			
			# Initialise CF and ACDD lists on first loop then check 
			# if variables the same between each file on subsequent loops. 
			if not cf:
				#meta = metadata.meta_check() 
				#print 'Process: '+str(cpu)+'   Initiating cf variable...'		
				cf = initCF(vars)	
			else:	
				#print  'Process: '+str(cpu)+'   updating cf variables...'
				cf.newvars(vars)			
			
			# ACDD Compliance Check
			meta.acddCheck(gatts)			# Check list against global file attributes, track sum of missing acdd attrs
			
			# Keep track of netCDF format
			meta.saveFormat(ncformat)		

			'''
			-------------------------------------------------------
			Wrapper for CF-Convention 'cfchecks.py' 
			-------------------------------------------------------'''
			# Search 'cfchecks.py' output for CF errors, warnings, and info messages
			with open (tmpfile, 'r') as tmpout:
				tmpout = tmpout.read().splitlines()
		
			# First find variable names/indices in output
			varlist = []
			varlist.append('global')
			lnnum = [] 
			lnnum.append(0)
			strtemp = 'Checking variable: '
			for i in range(0, len(tmpout[:-3])):			
				if tmpout[i].find(strtemp) != -1:
					varlist.append(tmpout[i][len(strtemp):])
					lnnum.append(i)
			# add index for end of file	
			lnnum.append(i)	
		
			# Now search between variable line numbers for associated errors
			# Note: warning/error 9.5 relates to cf_role and if error/warning present, it
			# becomes associated with last known variable unless separate search is called.	
			# Has to do with how cfchecks.py is written. Including these types of errors under 
			# what's called 'global'. 

			# Update Dec-2015: going to instead sum the 'okay' number of files to be consistent
			# with the other fields in the report
			for i in range(0, len(lnnum)-1):
				print >>tmplog, ' '
				currentVariable = varlist[i]
				err = warn = info = 0		
				for ltemp in tmpout[lnnum[i]:lnnum[i+1]]:
					### Checking error messages
					if ltemp.find('ERROR (9.5)') != -1:
						output.messages(tmplog, 'global', ltemp)
						err = 1	
					elif ltemp.find('ERROR') != -1:
						output.messages(tmplog, currentVariable, ltemp)
						err = 1

					### Checking warning messages
					elif ltemp.find('WARNING (9.5)') != -1:
						cf.warn['global'] = 1
						output.messages(tmplog, 'global', ltemp)
						warn = 1
					elif ltemp.find('WARNING') != -1:
						cf.warn[currentVariable] = 1
						output.messages(tmplog, currentVariable, ltemp)
						warn = 1

					### Checking info messages
					elif ltemp.find('INFO') != -1:
						cf.info[currentVariable] = 1
						output.messages(tmplog, currentVariable, ltemp)
						info = 1

				# If no errors, warnings or information messages found- add one count to the 
				# total number of successful files. Either way- increase counter on total
				# occurrances for this variable.
				cf.total[currentVariable] += 1
				if err == 0:
					cf.err[currentVariable] += 1
				if warn == 0:
					cf.warn[currentVariable] += 1
				if info == 0:
					cf.info[currentVariable] += 1
					
						
			print >>tmplog, ' \n'
			kk += 1
		except:
			break	

	try:					
		metaQ.put(meta)
		cfQ.put(cf)
		print 'Process: '+str(cpu)+' completed.'

	except UnboundLocalError, err1:
		print 'Process: '+str(cpu)+', UnBoundLocalError has occurred: ', err1

	except:
		print "Unexpected error: ", sys.exc_info()[0], sys.exc_info()[1]
 



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

 	
	def calc(self, result, nfiles):
		cflist = ['err', 'warn', 'info']
		for attr, score in self.__dict__.items():
			for key, item in result.__dict__[attr].items():	
				if attr in cflist:
					score += float(item)/result.__dict__['total'][key]
					
				elif key != 'total':
					score += float(item)/nfiles

			self.__dict__[attr] = round(score/len(result.__dict__[attr]), 2)



'''--------------------------------------------------------------
Main Program
--------------------------------------------------------------'''	
def main():
	start_time = datetime.now()

	# Make a temporary directory
	tmpdir = tempfile.mkdtemp(prefix='tmp', dir='.')

	'''--------------------------------------------------------------
	Get user inputs, initialise queues, and determine number of 
	processes to split jobs across. 
	--------------------------------------------------------------'''
	filesdir, file, ncpu, detailed_log, fn_out, debug = getinputs()	

	# Define queues for all the data/metadata reporting
	# that need saving from each process
	q = mp.Queue()
	fileList = []
	print "Searching directory and subdirectories for '.nc' files..."
	getAllFiles(filesdir, file, fileList, q)
	cf = mp.Queue()
	meta = mp.Queue()


	# If number of files is less than requested 'np', reduce to np = total # files
	if ncpu > len(fileList):
		ncpu = len(fileList)

	'''--------------------------------------------------------------
	Setup, run, join, and retrieve results for output
	--------------------------------------------------------------'''	
	# Print job info
	output.begin(filesdir, file, ncpu)

	# Setup a list of processes that we want to run
	print "Initiating multiprocesses..."
	processes = []
	for x in range(0, ncpu):
		p = mp.Process(target=worker, args=(x, q, cf, meta, tmpdir))
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
	CF = [cf.get() for p in processes]
	META = [meta.get() for p in processes]


	'''--------------------------------------------------------------
	Sum totals and print output
	--------------------------------------------------------------'''
	results = finalSum()
	for proc in range(0, ncpu):
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
	score.calc(results, len(fileList))

	
	'''--------------------------------------------------------------
	Print output to report and screen
	--------------------------------------------------------------'''	
	log, fn_out = output.header(fn_out, filesdir, file, len(fileList))
	output.report(results, score, log, len(fileList))
	output.screen(fn_out)
	output.append(tmpdir, fn_out, detailed_log, ncpu)


	'''--------------------------------------------------------------
	Cleanup and exit
	--------------------------------------------------------------'''
	# Either way, delete temp files before exiting (unless in debug mode)
	if debug == 0:
		print 'Removing temp files...'
		shutil.rmtree(tmpdir)
		print 'Done.'
	
	# Display total duration for compliance check 
	end_time = datetime.now()
	print('Duration: {}'.format(end_time - start_time))


if __name__ == '__main__':
	main()

