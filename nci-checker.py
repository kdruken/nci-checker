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


'''--------------------------------------------------------------
Help/usage message
--------------------------------------------------------------'''
def help():
	print '\n'
	print 'Usage: python ncichecker.py [OPTIONS] file/directory '
	print '-'*20, ' Options ', '-'*20 
	print "{:<20}{:<50}".format('\t --help', 'Print a usage message and exit')
	print "{:<20}{:<50}".format('\t --dir', 'Specifiy before directory to check entire contents')
	print "{:<20}{:<50}".format('\t --np', 'Specifiy the number of python multiprocesses to use (default np = 8)')
	print "{:<20}{:<50}".format('\t --log', 'Save detailed log output')
	print "{:<20}{:<50}".format('\t --brief', 'Save brief log output')
	print "{:<20}{:<50}".format('\t --fn', 'Specify prefix of log/brief filename')
	print '\n'

'''--------------------------------------------------------------
Get user inputs
--------------------------------------------------------------'''
def getinputs():
	# If no inputs given, print help info and exit
	if len(sys.argv) < 2:
		help()	
		sys.exit()
	
	# '--help', print how to use this tool
	helpStr = ['--help']
	for item in sys.argv:
		if item in helpStr:
			help() 
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
	if sys.argv.count('--n') == 1:
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
		

	return filesdir, file, ncpu, detailed_log, fn_out


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
Initialise 
--------------------------------------------------------------'''
class initCF(object):
	def __init__(self, vars):
		vars.append('global')
		self.err = dict.fromkeys(vars, 0)
		self.warn = dict.fromkeys(vars, 0)
		self.info = dict.fromkeys(vars, 0)


		
		
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
		

def sum(dict1, dict2):
	for item in dict2.keys():
		if item in dict1.keys():
			dict1[item] = dict1[item] + dict2[item]
		else:
			dict1[item] = dict2[item]
	
	

'''--------------------------------------------------------------
Check for particular standard variable name standards

** This is a modification to CF-compliance where new standard
variable libraries have been developed to expand CF-like
compliance for other geosciences.
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
def worker(cpu, chunkSize, q, cfQ, metaQ):  
	script = './checkerfiles/cfchecks2.py' 
	for kk in range(0, chunkSize):
		if q.empty() == False:
			ncfile = q.get()
			print 'PROC: ***', cpu, '*** Checking file:  ', kk+1, ' of ', chunkSize, '...'
			
			# Run the 'cfchecks.py' script on the individual file
			# Check for new standard name table first
			sn = stdNameTable()
			if not sn:
				os.system(script+' '+ncfile+' > temp'+str(cpu)+'.out')
			else:
				os.system(script+' -s '+sn+' '+ncfile+' > temp'+str(cpu)+'.out')
			
			templog = output.templog(cpu, ncfile)

			# Open/read file and extract global attributes, netCDF format
			gatts, ncformat, vars = readfile.read(ncfile)
			
			# Initialise lists when kk = 0
			if kk == 0:
				meta = metadata.meta_check() 		# Initialise list for tracking ACDD counts
				cf = initCF(vars)					# Initialise list for tracking CF messages
			
			# ACDD Compliance Check
			meta.acddCheck(gatts)			# Check list against global file attributes, track sum of missing acdd attrs
			
			# Keep track of netCDF format
			meta.saveFormat(ncformat)		

			'''
			-------------------------------------------------------
			Wrapper for CF-Convention 'cfchecks.py' 
			-------------------------------------------------------'''
			# Search 'cfchecks.py' output for CF errors, warnings, and info messages
			with open ('temp'+str(cpu)+'.out', 'r') as tempout:
				tempout = tempout.read().splitlines()
		
			# First find variable names/indices in output
			varlist = []
			varlist.append('global')
			lnnum = [] 
			lnnum.append(0)
			strtemp = 'Checking variable: '
			for i in range(0, len(tempout[:-3])):			
				if tempout[i].find(strtemp) != -1:
					varlist.append(tempout[i][len(strtemp):])
					lnnum.append(i)
			# add index for end of file	
			lnnum.append(i)	
		
			# Now search between variable line numbers for associated errors
			# Note: warning/error 9.5 relates to cf_role and if error/warning present, it
			# becomes associated with last known variable unless separate search is called.	
			# Has to do with how cfchecks.py is written.
			for i in range(0, len(lnnum)-1):
				print >>templog, ' '
				currentVariable = varlist[i]
				for ltemp in tempout[lnnum[i]:lnnum[i+1]]:
					### Checking error messages
					if ltemp.find('ERROR (9.5)') != -1:
						cf.err['global'] = cf.err['global'] + 1
						output.messages(templog, 'global', ltemp)
						
					elif ltemp.find('ERROR') != -1:
						cf.err[currentVariable] = cf.err[currentVariable] + 1
						output.messages(templog, currentVariable, ltemp)
	
					### Checking warning messages
					elif ltemp.find('WARNING (9.5)') != -1:
						cf.warn['global'] = cf.warn['global'] + 1
						output.messages(templog, 'global', ltemp)

					elif ltemp.find('WARNING') != -1:
						cf.warn[currentVariable] = cf.warn[currentVariable] + 1
						output.messages(templog, currentVariable, ltemp)

					### Checking info messages
					elif ltemp.find('INFO') != -1:
						cf.info[currentVariable] = cf.info[currentVariable] + 1
						output.messages(templog, currentVariable, ltemp)
					
						
			print >>templog, ' \n'
					
	metaQ.put(meta)
	cfQ.put(cf)




'''--------------------------------------------------------------
Main Program
--------------------------------------------------------------'''	
# def main():
start_time = datetime.now()



'''--------------------------------------------------------------
Get user inputs, initialise queues, and determine number of 
processes to split jobs across. 
--------------------------------------------------------------'''
filesdir, file, ncpu, detailed_log, fn_out = getinputs()	

# Define queues for all the data/metadata reporting
# that need saving from each process
q = mp.Queue()
fileList = []
getAllFiles(filesdir, file, fileList, q)
cf = mp.Queue()
meta = mp.Queue()


# Determine total number files per processor (chunkSize)
# Can use mp.cpu_count() to figure out #CPUs available if desired 
if ncpu > len(fileList):
	ncpu = len(fileList)
	chunkSize = 1
else:
	chunkSize = int(np.ceil(len(fileList)/float(ncpu)))


'''--------------------------------------------------------------
Setup, run, join, and retrieve results for output
--------------------------------------------------------------'''	
# Print job info
output.begin(filesdir, file, ncpu)

# Setup a list of processes that we want to run
processes = []
for x in range(0, ncpu):
	p = mp.Process(target=worker, args=(x, chunkSize, q, cf, meta))
	processes.append(p)

# Run processes
for p in processes:
	p.start()

# Exit the completed processes
for p in processes:
	p.join()

# Get process results from the output queue
CF = [cf.get() for p in processes]
META = [meta.get() for p in processes]


'''--------------------------------------------------------------
Sum totals and print output
--------------------------------------------------------------'''
results = finalSum()
for proc in range(0, ncpu):
	sum(results.req, META[proc].req)
	sum(results.rec, META[proc].rec)
	sum(results.sug, META[proc].sug)
	sum(results.other, META[proc].other)
	sum(results.format, META[proc].format)
	sum(results.err, CF[proc].err)
	sum(results.warn, CF[proc].warn)
	sum(results.info, CF[proc].info)


# Print output to report and screen
log, fn_out = output.header(fn_out, filesdir, file, len(fileList))
output.report(results, log, len(fileList))
output.screen(fn_out)
output.append(fn_out, detailed_log, ncpu)


'''--------------------------------------------------------------
Cleanup and exit
--------------------------------------------------------------'''
# Either way, delete temp files before exiting
for proc in range(0, ncpu):
	os.system('rm temp'+str(proc)+'.out')
	os.system('rm temp'+str(proc)+'.log')


end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))



# main()
